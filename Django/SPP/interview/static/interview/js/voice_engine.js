/**
 * VoiceEngine - Speech Recognition & Realistic Human Speech Synthesis
 * Manages voice input (STT), voice output (TTS), and audio waveform visualization.
 */

class VoiceEngine {
    constructor(callbacks = {}) {
        this.callbacks = callbacks; // onTranscriptUpdate, onSpeechStart, onSpeechEnd, onError

        // Speech Recognition setup
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.hasSTT = !!SpeechRecognition;
        this.recognition = this.hasSTT ? new SpeechRecognition() : null;

        if (this.recognition) {
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';

            this.setupSTTEvents();
        }

        // Speech Synthesis setup
        this.synth = window.speechSynthesis;
        this.hasTTS = !!this.synth;
        this.selectedVoice = null;

        if (this.hasTTS) {
            this.initVoice();
        }

        this.isListening = false;
        this.isSpeaking = false;
        this.fullTranscript = "";
        this.interimTranscript = "";
    }

    initVoice() {
        const loadVoices = () => {
            const voices = this.synth.getVoices();
            // Prefer natural human sounding English voices
            this.selectedVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Karen') || v.name.includes('Daniel'))) ||
                                voices.find(v => v.lang.startsWith('en')) ||
                                voices[0];
        };

        loadVoices();
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = loadVoices;
        }
    }

    setupSTTEvents() {
        if (!this.recognition) return;

        this.recognition.onresult = (event) => {
            let interim = '';
            let finalStr = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalStr += transcript + ' ';
                } else {
                    interim += transcript;
                }
            }

            if (finalStr) {
                this.fullTranscript += finalStr;
            }
            this.interimTranscript = interim;

            const combined = (this.fullTranscript + ' ' + this.interimTranscript).trim();
            if (this.callbacks.onTranscriptUpdate) {
                this.callbacks.onTranscriptUpdate(combined);
            }
        };

        this.recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            if (event.error !== 'no-speech' && this.callbacks.onError) {
                this.callbacks.onError(event.error);
            }
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                // Auto restart if user is still in listening mode
                try {
                    this.recognition.start();
                } catch (e) {
                    // Ignore restart collision
                }
            }
        };
    }

    startListening() {
        if (!this.hasSTT) {
            console.warn("SpeechRecognition API not supported in this browser. Falling back to text mode.");
            return false;
        }

        this.fullTranscript = "";
        this.interimTranscript = "";
        this.isListening = true;

        try {
            this.recognition.start();
            return true;
        } catch (e) {
            console.warn("STT already active or starting:", e);
            return true;
        }
    }

    stopListening() {
        this.isListening = false;
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (e) {
                // Ignore
            }
        }
        return this.fullTranscript.trim();
    }

    speak(text, onComplete = null) {
        if (!this.hasTTS) {
            console.warn("SpeechSynthesis not supported.");
            if (onComplete) onComplete();
            return;
        }

        // Cancel ongoing speech
        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        if (this.selectedVoice) {
            utterance.voice = this.selectedVoice;
        }

        utterance.rate = 0.95;  // Conversational human cadence
        utterance.pitch = 1.0;  // Natural pitch

        utterance.onstart = () => {
            this.isSpeaking = true;
            if (this.callbacks.onSpeechStart) {
                this.callbacks.onSpeechStart();
            }
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            if (this.callbacks.onSpeechEnd) {
                this.callbacks.onSpeechEnd();
            }
            if (onComplete) {
                onComplete();
            }
        };

        utterance.onerror = (err) => {
            console.error("Speech synthesis error:", err);
            this.isSpeaking = false;
            if (this.callbacks.onSpeechEnd) {
                this.callbacks.onSpeechEnd();
            }
            if (onComplete) {
                onComplete();
            }
        };

        this.synth.speak(utterance);
    }

    stopSpeaking() {
        if (this.hasTTS) {
            this.synth.cancel();
            this.isSpeaking = false;
            if (this.callbacks.onSpeechEnd) {
                this.callbacks.onSpeechEnd();
            }
        }
    }
}

window.VoiceEngine = VoiceEngine;
