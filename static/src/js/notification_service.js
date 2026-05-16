/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * Convert ALL-CAPS words to Title Case so TTS reads full names instead of
 * spelling them letter-by-letter. Common with Ghanaian patient names stored
 * in uppercase, e.g. "KWAME ASANTE" → "Kwame Asante".
 */
function toSpeakable(text) {
    return text.replace(/\b([A-Z]{2,})\b/g, (word) => {
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    });
}

export const medisiteNotificationService = {
    dependencies: ["bus_service", "mail.sound_effects", "notification"],
    start(env, { bus_service, "mail.sound_effects": soundEffects, notification }) {

        bus_service.addChannel("medisite_notification");
        bus_service.subscribe("medisite_notification", (payload) => {
            console.info("Medisite Notification Received:", payload);

            // 1. Play Alert Sound
            soundEffects.play("new-message");

            // 2. Show UI Notification
            notification.add(payload.message, {
                title: _t("Clinic Workflow Alert"),
                type: "info",
                sticky: false,
            });

            // 3. Role-Specific Voice (TTS)
            if ('speechSynthesis' in window) {
                // Normalize ALL-CAPS patient names so TTS reads words, not letters
                const speakText = toSpeakable(payload.message);

                const speakMessage = () => {
                    const utterance = new SpeechSynthesisUtterance(speakText);
                    const voices = window.speechSynthesis.getVoices();

                    const roleConfig = {
                        'doctor':   { pitch: 0.9, rate: 0.65, volume: 1.0 },
                        'nurse':    { pitch: 1.2, rate: 0.75, volume: 1.0 },
                        'lab':      { pitch: 0.8, rate: 0.70, volume: 1.0 },
                        'pharmacy': { pitch: 1.0, rate: 0.70, volume: 1.0 }
                    };

                    const config = roleConfig[payload.role] || { pitch: 1.0, rate: 0.7, volume: 1.0 };
                    utterance.pitch = config.pitch;
                    utterance.rate  = config.rate;
                    utterance.volume = config.volume;

                    if (voices.length > 0) {
                        const feminineVoice = voices.find(v =>
                            v.lang.startsWith("en") &&
                            (v.name.includes("Female") || v.name.includes("-f") || v.name.includes("+f") ||
                             v.name.includes("Zira") || v.name.includes("Samantha") || v.name.includes("Google US English"))
                        ) || voices.find(v => v.lang.startsWith("en") && !v.name.includes("Male"));

                        utterance.voice = feminineVoice || voices.find(v => v.lang.startsWith("en")) || voices[0];

                        if (!feminineVoice) {
                            utterance.pitch = Math.min(utterance.pitch + 0.3, 1.5);
                        }
                    }

                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                };

                if (window.speechSynthesis.getVoices().length === 0) {
                    window.speechSynthesis.onvoiceschanged = speakMessage;
                }
                setTimeout(speakMessage, 1000);
            }
        });
    },
};

registry.category("services").add("medisite_clinic.notification_service", medisiteNotificationService);
