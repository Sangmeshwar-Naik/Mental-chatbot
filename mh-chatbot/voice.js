// ========================================
// Voice Functionality - Speech Recognition & Synthesis
// ========================================

let recognition = null;
let synthesis = window.speechSynthesis;
let isRecording = false;
let voiceOutputEnabled = true;

const micButton = document.getElementById('micButton');
const micIcon = document.getElementById('micIcon');
const speakerButton = document.getElementById('speakerButton');
const speakerIcon = document.getElementById('speakerIcon');
const voiceStatus = document.getElementById('voiceStatus');

// Store original addMessage function
const originalAddMessage = window.addMessage;

// Check browser support for speech recognition
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        setupRecognitionHandlers();
        updateVoiceStatus('Voice input ready! 🎤 Click mic to speak');
        setTimeout(() => updateVoiceStatus(''), 3000);
    } else {
        micButton.disabled = true;
        micButton.style.opacity = '0.5';
        updateVoiceStatus('Voice input not supported in this browser');
        console.warn('Speech recognition not supported');
    }
}

// Setup recognition event handlers
function setupRecognitionHandlers() {
    recognition.onstart = () => {
        isRecording = true;
        micButton.classList.add('recording');
        micIcon.textContent = '🔴';
        updateVoiceStatus('Listening... Speak now');
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }

        const messageInput = document.getElementById('messageInput');

        // Show interim results in input
        if (interimTranscript) {
            messageInput.value = interimTranscript;
        }

        // Send final transcript
        if (finalTranscript) {
            messageInput.value = finalTranscript.trim();
            updateVoiceStatus('Voice input captured ✓');

            // Auto-send after a brief delay
            setTimeout(() => {
                if (messageInput.value.trim() && window.sendMessage) {
                    window.sendMessage();
                }
            }, 500);
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopRecording();

        if (event.error === 'no-speech') {
            updateVoiceStatus('No speech detected. Try again.');
        } else if (event.error === 'not-allowed') {
            updateVoiceStatus('Microphone access denied. Allow microphone access in browser settings.');
        } else {
            updateVoiceStatus('Error: ' + event.error);
        }

        setTimeout(() => updateVoiceStatus(''), 3000);
    };

    recognition.onend = () => {
        stopRecording();
    };
}

// Toggle voice recording
function toggleRecording() {
    if (!recognition) {
        updateVoiceStatus('Voice input not available');
        return;
    }

    if (isRecording) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            updateVoiceStatus('Could not start voice input');
        }
    }
}

// Stop recording
function stopRecording() {
    isRecording = false;
    micButton.classList.remove('recording');
    micIcon.textContent = '🎤';
}

// Speak text using Text-to-Speech
function speakText(text) {
    if (!synthesis || !voiceOutputEnabled) return;

    // Cancel any ongoing speech
    synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.lang = 'en-US';

    utterance.onstart = () => {
        speakerButton.classList.add('speaking');
    };

    utterance.onend = () => {
        speakerButton.classList.remove('speaking');
    };

    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        speakerButton.classList.remove('speaking');
    };

    synthesis.speak(utterance);
}

// Toggle voice output
function toggleVoiceOutput() {
    voiceOutputEnabled = !voiceOutputEnabled;

    if (voiceOutputEnabled) {
        speakerIcon.textContent = '🔊';
        updateVoiceStatus('Voice output enabled - AI will speak responses');
    } else {
        speakerIcon.textContent = '🔇';
        updateVoiceStatus('Voice output muted');
        synthesis.cancel();
    }

    setTimeout(() => {
        updateVoiceStatus('');
    }, 2000);
}

// Update voice status display
function updateVoiceStatus(message) {
    voiceStatus.textContent = message;
}

// Intercept addMessage to support voice output
if (window.addMessage) {
    const originalAdd = window.addMessage;
    window.addMessage = function (content, isUser = false) {
        originalAdd(content, isUser);

        // Speak AI responses if voice output is enabled
        if (!isUser && voiceOutputEnabled) {
            // Small delay to ensure message is displayed first
            setTimeout(() => speakText(content), 100);
        }
    };
}

// Event listeners for voice buttons
if (micButton) {
    micButton.addEventListener('click', toggleRecording);
}

if (speakerButton) {
    speakerButton.addEventListener('click', toggleVoiceOutput);
}

// Initialize voice recognition when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceRecognition);
} else {
    initVoiceRecognition();
}

// Stop speech when user starts typing
const messageInput = document.getElementById('messageInput');
if (messageInput) {
    messageInput.addEventListener('input', () => {
        if (synthesis && synthesis.speaking) {
            synthesis.cancel();
            speakerButton.classList.remove('speaking');
        }
    });
}

console.log('Voice functionality loaded! 🎤🔊');
