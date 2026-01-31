(() => {
    'use strict';

    let currentSpeechUtterance = null;
    let voices = [];
    let speakQueue = [];

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

    function normalizeText(text) {
        return text
            .replace(/\s+/g, ' ')
            .replace(/([.!?。！？])(?=\S)/g, '$1 ')
            .trim();
    }

    function countMatches(text, regex) {
        const m = text.match(regex);
        return m ? m.length : 0;
    }

    function detectLang(text) {
        const jaCount = countMatches(text, /[\u3040-\u30ff\u3400-\u9fff]/g);
        const enCount = countMatches(text, /[A-Za-z]/g);
        if (jaCount === 0 && enCount === 0) return 'ja-JP';
        return jaCount >= enCount ? 'ja-JP' : 'en-US';
    }

    function splitBySentence(text) {
        const parts = [];
        const tokens = text.split(/([.!?。！？\n]+)/).filter(Boolean);
        for (let i = 0; i < tokens.length; i += 2) {
            const sentence = (tokens[i] || '') + (tokens[i + 1] || '');
            const trimmed = sentence.trim();
            if (trimmed) parts.push(trimmed);
        }
        return parts.length ? parts : [text];
    }

    function splitByLanguage(text) {
        const chunks = [];
        let buffer = '';
        let currentLang = null;

        for (const char of text) {
            const lang = detectLang(char);
            if (!currentLang) currentLang = lang;
            if (lang !== currentLang) {
                if (buffer.trim()) {
                    chunks.push({ text: buffer.trim(), lang: currentLang });
                }
                buffer = char;
                currentLang = lang;
            } else {
                buffer += char;
            }
        }

        if (buffer.trim()) {
            chunks.push({ text: buffer.trim(), lang: currentLang });
        }

        return chunks.length ? chunks : [{ text, lang: detectLang(text) }];
    }

    function preferredNames(lang) {
        if (lang === 'ja-JP') {
            return [
                'Google 日本語',
                'Google Japanese',
                'Microsoft Haruka',
                'Microsoft Ayumi',
                'Microsoft Sayaka',
                'Kyoko',
                'Otoya',
                'Siri',
                'Premium',
                'Enhanced'
            ];
        }
        if (lang === 'en-US') {
            return [
                'Google US English',
                'Google English',
                'Microsoft Zira',
                'Microsoft Aria',
                'Microsoft Jenny',
                'Samantha',
                'Alex',
                'Siri',
                'Premium',
                'Enhanced'
            ];
        }
        return ['Google', 'Microsoft', 'Siri', 'Premium', 'Enhanced'];
    }

    function scoreVoice(voice, lang) {
        let score = 0;
        if (voice.lang === lang) score += 3;
        if (voice.lang.startsWith(lang.substring(0, 2))) score += 1;
        if (voice.localService) score += 1;
        const name = voice.name.toLowerCase();
        if (name.includes('google') || name.includes('microsoft') || name.includes('enhanced')) score += 2;
        if (name.includes('premium')) score += 2;
        if (name.includes('compact')) score -= 1;
        return score;
    }

    function pickVoice(lang) {
        if (!voices.length) return null;
        const preferred = preferredNames(lang).map(v => v.toLowerCase());
        for (const pref of preferred) {
            const match = voices.find(v => v.lang.startsWith(lang.substring(0, 2)) && v.name.toLowerCase().includes(pref));
            if (match) return match;
        }
        const sorted = [...voices].sort((a, b) => scoreVoice(b, lang) - scoreVoice(a, lang));
        return sorted[0] || null;
    }

    function buildQueue(text, lang, rate) {
        const normalized = normalizeText(text);
        const sentences = splitBySentence(normalized);
        const queue = [];

        if (lang === 'auto') {
            for (const sentence of sentences) {
                const chunks = splitByLanguage(sentence);
                for (const chunk of chunks) {
                    if (chunk.text) {
                        queue.push({ text: chunk.text, lang: chunk.lang, rate });
                    }
                }
            }
        } else {
            for (const sentence of sentences) {
                if (sentence) queue.push({ text: sentence, lang, rate });
            }
        }

        return queue;
    }

    function speakNext() {
        if (!speakQueue.length) {
            currentSpeechUtterance = null;
            return;
        }

        const item = speakQueue.shift();
        const utterance = new SpeechSynthesisUtterance(item.text);
        utterance.lang = item.lang;
        utterance.rate = Math.max(0.5, Math.min(2, item.rate || 1));
        utterance.pitch = 1;
        utterance.volume = 1;

        const selectedVoice = pickVoice(item.lang);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log('🎙️ Selected voice:', selectedVoice.name, selectedVoice.lang);
        }

        utterance.onstart = () => {
            console.log('▶️ Speech started');
        };

        utterance.onend = () => {
            console.log('⏹️ Speech ended');
            currentSpeechUtterance = null;
            speakNext();
        };

        utterance.onerror = (event) => {
            if (event.error !== 'canceled') {
                console.error('❌ Speech error:', event.error);
                alert('読み上げエラー: ' + event.error);
            } else {
                console.log('ℹ️ Previous utterance cancelled');
            }
            currentSpeechUtterance = null;
            speakQueue = [];
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
    }

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

            speakQueue = buildQueue(text, lang, rate);
            speakNext();
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
        speakQueue = [];
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
