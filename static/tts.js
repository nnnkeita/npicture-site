(() => {
    'use strict';

    let currentSpeechUtterance = null;
    let voices = [];

    function initVoices() {
        if (window.speechSynthesis) {
            voices = window.speechSynthesis.getVoices();
            console.log('🎙️ Available voices:', voices.map(v => `${v.name} (${v.lang})`));

            window.speechSynthesis.onvoiceschanged = () => {
                voices = window.speechSynthesis.getVoices();
                console.log('🎙️ Voices updated:', voices.map(v => `${v.name} (${v.lang})`));
            };
        }
    }

    window.addEventListener('load', initVoices);
    initVoices();

    function speakBlock(blockId) {
        try {
            console.log('📢 speakBlock called with blockId:', blockId);

            const blockDiv = document.querySelector(`[data-id="${blockId}"]`);
            if (!blockDiv) {
                console.error('❌ Block not found:', blockId);
                return;
            }

            const textarea = blockDiv.querySelector('textarea');
            if (!textarea) {
                console.error('❌ Textarea not found in block:', blockId);
                return;
            }

            const text = textarea.value.trim();
            if (!text) {
                alert('読み上げるテキストを入力してください');
                return;
            }

            console.log('📝 Text to speak:', text);

            if (!window.speechSynthesis) {
                alert('このブラウザは読み上げ機能をサポートしていません');
                return;
            }

            const langSelect = document.getElementById(`speak-lang-${blockId}`);
            const rateInput = document.getElementById(`speak-rate-${blockId}`);
            const lang = langSelect ? langSelect.value : 'ja-JP';
            const rate = rateInput ? parseFloat(rateInput.value) : 1;

            console.log('🌍 Language:', lang, '⚡ Rate:', rate);

            if (currentSpeechUtterance) {
                currentSpeechUtterance.onerror = null;
                window.speechSynthesis.cancel();
                console.log('⏸️ Cancelled previous utterance');
            }

            let selectedVoice = null;
            if (voices.length > 0) {
                selectedVoice = voices.find(voice => voice.lang === lang);
                if (!selectedVoice) {
                    selectedVoice = voices.find(voice => voice.lang.startsWith(lang.substring(0, 2)));
                }
                if (!selectedVoice) {
                    selectedVoice = voices[0];
                }
                console.log('🎙️ Selected voice:', selectedVoice.name, selectedVoice.lang);
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = Math.max(0.5, Math.min(2, rate || 1));
            utterance.pitch = 1;
            utterance.volume = 1;

            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }

            utterance.onstart = () => {
                console.log('▶️ Speech started');
            };

            utterance.onend = () => {
                console.log('⏹️ Speech ended');
                currentSpeechUtterance = null;
            };

            utterance.onerror = (event) => {
                if (event.error !== 'canceled') {
                    console.error('❌ Speech error:', event.error);
                    alert('読み上げエラー: ' + event.error);
                } else {
                    console.log('ℹ️ Previous utterance cancelled');
                }
            };

            utterance.onpause = () => {
                console.log('⏸️ Speech paused');
            };

            utterance.onresume = () => {
                console.log('▶️ Speech resumed');
            };

            currentSpeechUtterance = utterance;
            window.speechSynthesis.speak(utterance);
            console.log('🔊 Speech synthesis queued');
        } catch (error) {
            console.error('❌ speakBlock failed:', error);
            alert('読み上げ機能の初期化に失敗しました');
        }
    }

    function stopSpeaking() {
        console.log('⏹️ Stopping speech');
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            console.log('🛑 Speech cancelled');
        }
        currentSpeechUtterance = null;
    }

    function updateSpeakLang(blockId, lang) {
        console.log('🌍 Updating language:', blockId, lang);
        const rateInput = document.getElementById(`speak-rate-${blockId}`);
        const rate = rateInput ? parseFloat(rateInput.value) : 1;
        const props = {
            lang: lang,
            rate: rate
        };
        if (typeof window.updateBlock === 'function') {
            window.updateBlock(blockId, 'props', JSON.stringify(props));
        } else {
            console.warn('updateBlock is not available yet');
        }
    }

    function updateSpeakRate(blockId, rate) {
        console.log('⚡ Updating rate:', blockId, rate);
        const rateValue = parseFloat(rate);
        const displayEl = document.getElementById(`speak-rate-display-${blockId}`);
        if (displayEl) {
            displayEl.textContent = rateValue.toFixed(1) + 'x';
        }

        const langSelect = document.getElementById(`speak-lang-${blockId}`);
        const lang = langSelect ? langSelect.value : 'ja-JP';
        const props = {
            lang: lang,
            rate: rateValue
        };
        if (typeof window.updateBlock === 'function') {
            window.updateBlock(blockId, 'props', JSON.stringify(props));
        } else {
            console.warn('updateBlock is not available yet');
        }
    }

    window.speakBlock = speakBlock;
    window.stopSpeaking = stopSpeaking;
    window.updateSpeakLang = updateSpeakLang;
    window.updateSpeakRate = updateSpeakRate;
})();
