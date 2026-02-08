(function() {
    'use strict';

    // カロリープロパティキャッシュ
    const caloriePropsCache = {};
    const calorieDebounce = new Map();

    // カロリー結果をレンダリング
    function renderCalorieResult(blockId, data) {
        if (!data) return;
        const r = data.result || data;
        if (!r) return;

        const totalEl = document.getElementById(`cal-total-${blockId}`);
        if (totalEl && r.total_kcal !== undefined) {
            totalEl.textContent = `${r.total_kcal} kcal`;
        }

        const itemsEl = document.getElementById(`cal-items-${blockId}`);
        if (itemsEl && Array.isArray(r.items)) {
            itemsEl.innerHTML = r.items.length
                ? r.items.map(item => {
                    const mark = item.source === 'web'
                        ? '（web）'
                        : (item.is_estimated ? '（推定）' : '');
                    return `<div>${item.input} → ${item.kcal} kcal ${mark}</div>`;
                }).join('')
                : '';
        }

        const legacyDiv = document.querySelector(`[data-block-id="${blockId}"] .calorie-result`);
        if (legacyDiv) {
            legacyDiv.innerHTML = `合計: ${r.total_kcal ?? '-'} kcal`;
        }
    }

    // カロリー入力処理
    function handleCalorieInput(blockId, value) {
        const lines = String(value || '').split('\n').map(line => line.trim()).filter(Boolean);
        requestCalorieCalc(blockId, { lines });
    }

    function getCalorieEntries(blockId) {
        caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
        const props = caloriePropsCache[blockId];
        if (Array.isArray(props.entries) && props.entries.length > 0) {
            return props.entries;
        }
        const raw = props.rawText || '';
        const lines = String(raw || '').split('\n').map(line => line.trim()).filter(Boolean);
        const entries = lines.length ? lines.map(line => ({ name: line, amount: '', unit: '' })) : [{ name: '', amount: '', unit: '' }];
        props.entries = entries;
        return entries;
    }

    function setCalorieEntries(blockId, entries) {
        caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
        caloriePropsCache[blockId].entries = entries;
        scheduleCalorieSave(blockId);
    }

    function renderCalorieRows(blockId) {
        const container = document.getElementById(`cal-rows-${blockId}`);
        if (!container) return;
        const entries = getCalorieEntries(blockId);
        container.innerHTML = entries.map((entry, idx) => {
            const name = entry.name || '';
            const amount = entry.amount ?? '';
            const unit = entry.unit || '';
            return `
                <div class="flex items-center gap-2 cal-row" data-index="${idx}">
                    <input type="text" class="flex-1 border border-green-100 rounded px-2 py-1 text-sm" placeholder="品名" value="${name.replace(/"/g, '&quot;')}" oninput="updateCalorieEntry(${blockId}, ${idx}, 'name', this.value)">
                    <input type="number" class="w-20 border border-green-100 rounded px-2 py-1 text-sm" placeholder="量" value="${amount}" oninput="updateCalorieEntry(${blockId}, ${idx}, 'amount', this.value)">
                    <input type="text" class="w-20 border border-green-100 rounded px-2 py-1 text-sm" placeholder="単位" value="${unit.replace(/"/g, '&quot;')}" oninput="updateCalorieEntry(${blockId}, ${idx}, 'unit', this.value)">
                    <button type="button" class="text-gray-400 hover:text-red-500" onclick="removeCalorieRow(${blockId}, ${idx})">×</button>
                </div>
            `;
        }).join('');
    }

    function updateCalorieEntry(blockId, index, field, value) {
        const entries = getCalorieEntries(blockId).slice();
        if (!entries[index]) return;
        entries[index] = { ...entries[index], [field]: value };
        setCalorieEntries(blockId, entries);
        requestCalorieCalc(blockId, { items: entries });
    }

    function addCalorieRow(blockId) {
        const entries = getCalorieEntries(blockId).slice();
        entries.push({ name: '', amount: '', unit: '' });
        setCalorieEntries(blockId, entries);
        renderCalorieRows(blockId);
    }

    function removeCalorieRow(blockId, index) {
        const entries = getCalorieEntries(blockId).slice();
        if (entries.length <= 1) {
            entries[0] = { name: '', amount: '', unit: '' };
        } else {
            entries.splice(index, 1);
        }
        setCalorieEntries(blockId, entries);
        renderCalorieRows(blockId);
        requestCalorieCalc(blockId, { items: entries });
    }

    function scheduleCalorieSave(blockId) {
        if (calorieDebounce.has(blockId)) {
            clearTimeout(calorieDebounce.get(blockId));
        }
        const timeoutId = setTimeout(() => {
            fetch(`/api/blocks/${blockId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ props: JSON.stringify(caloriePropsCache[blockId]) })
            }).catch(err => console.warn('Failed to save calorie props:', err));
            calorieDebounce.delete(blockId);
        }, 500);
        calorieDebounce.set(blockId, timeoutId);
    }

    function requestCalorieCalc(blockId, payload) {
        fetch('/api/calc-calories', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            renderCalorieResult(blockId, data);
            if (data && data.total_kcal !== undefined) {
                caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
                caloriePropsCache[blockId].total_kcal = data.total_kcal;
                caloriePropsCache[blockId].items = data.items || [];
                if (data.note) caloriePropsCache[blockId].note = data.note;
                scheduleCalorieSave(blockId);
            }
        })
        .catch(err => {
            console.error('Calorie calculation error:', err);
            const itemsEl = document.getElementById(`cal-items-${blockId}`);
            if (itemsEl) {
                itemsEl.innerHTML = '<div style="color:red">カロリー計算エラー</div>';
            }
        });
    }

    // カロリータイトル更新
    function updateCalorieTitle(blockId, title) {
        caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
        caloriePropsCache[blockId].title = title;
    }

    // カロリーボックス追加
    function addCalorieBox(blockId) {
        if (typeof addBlockAfter === 'function') {
            addBlockAfter(blockId, 'calorie');
        } else {
            console.error('addBlockAfter function not found');
        }
    }

    // グローバル公開
    window.renderCalorieResult = renderCalorieResult;
    window.handleCalorieInput = handleCalorieInput;
    window.updateCalorieTitle = updateCalorieTitle;
    window.addCalorieBox = addCalorieBox;
    window.caloriePropsCache = caloriePropsCache;
    window.renderCalorieRows = renderCalorieRows;
    window.updateCalorieEntry = updateCalorieEntry;
    window.addCalorieRow = addCalorieRow;
    window.removeCalorieRow = removeCalorieRow;

})();
