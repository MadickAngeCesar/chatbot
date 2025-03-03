import json
import os

class Translator:
    """
    A translator class to enable multilingual support in the chatbot application.
    Manages translations between English and French.
    """
    
    def __init__(self):
        """Initialize the translator with English and French translations."""
        self.translations = {
            'en': {
                'window_title': 'Madick Chatbot',
                'ready': 'Ready',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'success': 'Success',
                'chat': '💬 Chat',
                'templates': '📋 Templates',
                'history': '📚 History',
                'files': '📁 Files',
                'settings': '⚙️ Settings',
                'model': 'Model:',
                'session': 'Session:',
                'clear': '🗑️ Clear',
                'export': '📤 Export',
                'start_recording': 'Start Recording',
                'stop_recording': 'Stop Recording',
                'template': 'Template:',
                'send': '📩 Send',
                'you': 'You',
                'ai': 'AI',
                'available_templates': 'Available Templates',
                'none': 'None',
                'custom': 'Custom...',
                'new_template': 'New Template',
                'template_name': 'Template Name:',
                'template_prompt': 'Enter the template prompt (use {input} for user input):',
                'template_description': 'Enter a short description:',
                'template_category': 'Select or enter a category:',
                'search_placeholder': 'Search in chat history...',
                'refresh': '🔄 Refresh',
                'clear_history': '🗑️ Clear History',
                'user': 'User',
                'uploaded_files': 'Uploaded Files',
                'upload_file': '📎 Upload File',
                'attach_file': '📎 Attach File',
                'file_attached': 'File Attached',
                'binary_file': 'Binary File',
                'file_too_large': 'File Too Large',
                'invalid_json': 'Invalid JSON',
                'binary_file_detected': 'Binary File Detected',
                'error_reading_file': 'Error Reading File',
                'voice_input': 'Voice Input',
                'recording_start_prompt': 'Press Start to begin recording...',
                'initializing_mic': 'Initializing microphone...',
                'listening': 'Listening...',
                'processing_speech': 'Processing speech...',
                'recording_stopped': 'Recording stopped',
                'recording_success': 'Recording successful!',
                'cancel': 'Cancel',
                'message_copied': 'Message copied to clipboard',
                'message_edit_ready': 'Message ready for editing',
                'tts_future': 'This feature will be implemented in a future update.',
                'response_saved_db': 'Response saved to history',
                'response_saved_file': 'Response saved to {filename}',
                'error_saving_db': 'Error saving to database: {error}',
                'error_saving_file': 'Error saving file: {error}',
                'switched_model': 'Switched to {model} model',
                'switched_session': 'Switched to session: {session}',
                'clear_chat_confirm': 'Are you sure you want to clear the chat history?',
                'clear_history_confirm': 'Are you sure you want to clear all chat history?',
                'history_cleared': 'Chat history cleared successfully',
                'error_history': 'Error clearing history: {error}',
                'minimized': 'ChatBot Minimized',
                'still_running': 'Application is still running in the system tray.',
                'voice_error': 'Voice input error: {error}',
                'new_session': 'New Session',
                'session_name': 'Enter session name:',
                'session_exists': 'Session name already exists!',
                'delete_template': 'Delete Template',
                'delete_template_confirm': 'Are you sure you want to delete the template \'{name}\'?',
                'template_deleted': 'Template \'{name}\' deleted successfully',
                'template_created': 'Template \'{name}\' created successfully',
                'error_template': 'Error {action} template: {error}',
                'content_of_file': 'Content of {filename}:',
                'send_file_confirm': 'Do you want to send the contents of {filename} to the AI?',
                'file_content_added': 'File content added to input',
                'binary_file_info': '{filename} is a binary file. Only the file reference will be added.',
                'attached_file': '[Attached file: {filename}]',
                'file_attached_status': 'File \'{filename}\' attached',
                'no_mic': 'No microphone detected',
                'speech_not_understood': 'Could not understand audio. Please speak more clearly',
                'service_error': 'Service error: {error}',
                'recording_error': 'Recording error: {error}',
                'language_changed': 'Language changed to {language}'
            },
            'fr': {
                'window_title': 'Madick Chatbot',
                'ready': 'Prêt',
                'error': 'Erreur',
                'warning': 'Avertissement',
                'info': 'Information',
                'success': 'Succès',
                'chat': '💬 Discuter',
                'templates': '📋 Modèles',
                'history': '📚 Historique',
                'files': '📁 Fichiers',
                'settings': '⚙️ Paramètres',
                'model': 'Modèle:',
                'session': 'Session:',
                'clear': '🗑️ Effacer',
                'export': '📤 Exporter',
                'start_recording': 'Commencer l\'enregistrement',
                'stop_recording': 'Arrêter l\'enregistrement',
                'template': 'Modèle:',
                'send': '📩 Envoyer',
                'you': 'Vous',
                'ai': 'IA',
                'available_templates': 'Modèles disponibles',
                'none': 'Aucun',
                'custom': 'Personnalisé...',
                'new_template': 'Nouveau modèle',
                'template_name': 'Nom du modèle:',
                'template_prompt': 'Entrez le modèle (utilisez {input} pour l\'entrée utilisateur):',
                'template_description': 'Entrez une courte description:',
                'template_category': 'Sélectionnez ou entrez une catégorie:',
                'search_placeholder': 'Rechercher dans l\'historique...',
                'refresh': '🔄 Rafraîchir',
                'clear_history': '🗑️ Effacer l\'historique',
                'user': 'Utilisateur',
                'uploaded_files': 'Fichiers téléchargés',
                'upload_file': '📎 Télécharger un fichier',
                'attach_file': '📎 Joindre un fichier',
                'file_attached': 'Fichier joint',
                'binary_file': 'Fichier binaire',
                'file_too_large': 'Fichier trop volumineux',
                'invalid_json': 'JSON invalide',
                'binary_file_detected': 'Fichier binaire détecté',
                'error_reading_file': 'Erreur de lecture du fichier',
                'voice_input': 'Entrée vocale',
                'recording_start_prompt': 'Appuyez sur Démarrer pour commencer l\'enregistrement...',
                'initializing_mic': 'Initialisation du microphone...',
                'listening': 'Écoute en cours...',
                'processing_speech': 'Traitement de la parole...',
                'recording_stopped': 'Enregistrement arrêté',
                'recording_success': 'Enregistrement réussi!',
                'cancel': 'Annuler',
                'message_copied': 'Message copié dans le presse-papiers',
                'message_edit_ready': 'Message prêt pour l\'édition',
                'tts_future': 'Cette fonctionnalité sera implémentée dans une future mise à jour.',
                'response_saved_db': 'Réponse sauvegardée dans l\'historique',
                'response_saved_file': 'Réponse sauvegardée dans {filename}',
                'error_saving_db': 'Erreur lors de la sauvegarde dans la base de données: {error}',
                'error_saving_file': 'Erreur lors de la sauvegarde du fichier: {error}',
                'switched_model': 'Passage au modèle {model}',
                'switched_session': 'Session changée: {session}',
                'clear_chat_confirm': 'Êtes-vous sûr de vouloir effacer l\'historique de discussion?',
                'clear_history_confirm': 'Êtes-vous sûr de vouloir effacer tout l\'historique de discussion?',
                'history_cleared': 'Historique de discussion effacé avec succès',
                'error_history': 'Erreur lors de l\'effacement de l\'historique: {error}',
                'minimized': 'ChatBot Minimisé',
                'still_running': 'L\'application est toujours en cours d\'exécution dans la barre d\'état système.',
                'voice_error': 'Erreur d\'entrée vocale: {error}',
                'new_session': 'Nouvelle Session',
                'session_name': 'Entrez le nom de la session:',
                'session_exists': 'Le nom de la session existe déjà!',
                'delete_template': 'Supprimer le modèle',
                'delete_template_confirm': 'Êtes-vous sûr de vouloir supprimer le modèle \'{name}\'?',
                'template_deleted': 'Modèle \'{name}\' supprimé avec succès',
                'template_created': 'Modèle \'{name}\' créé avec succès',
                'error_template': 'Erreur lors {action} du modèle: {error}',
                'content_of_file': 'Contenu du fichier {filename}:',
                'send_file_confirm': 'Voulez-vous envoyer le contenu de {filename} à l\'IA?',
                'file_content_added': 'Contenu du fichier ajouté à l\'entrée',
                'binary_file_info': '{filename} est un fichier binaire. Seule la référence au fichier sera ajoutée.',
                'attached_file': '[Fichier joint: {filename}]',
                'file_attached_status': 'Fichier \'{filename}\' joint',
                'no_mic': 'Aucun microphone détecté',
                'speech_not_understood': 'Impossible de comprendre l\'audio. Veuillez parler plus clairement',
                'service_error': 'Erreur de service: {error}',
                'recording_error': 'Erreur d\'enregistrement: {error}',
                'language_changed': 'Langue changée en {language}'
            }
        }
        
        self.current_language = 'en'
        
        # Try to load language setting from settings file
        self._load_language_from_settings()
    
    def _load_language_from_settings(self):
        """Load language setting from the settings file if it exists."""
        
        try:
            pass
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'language' in settings:
                        self.set_language(settings['language'])
        except Exception as e:
            # In case of any error, fallback to English
            print(f"Error loading language settings: {e}")
            self.current_language = 'en'
    
    def reload_settings(self):
        """Reload language settings from settings file."""
        self._load_language_from_settings()
    
    def set_language(self, language_code):
        """Set the current language."""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        else:
            print(f"Language '{language_code}' not supported. Using English.")
            self.current_language = 'en'
            return False
    
    def get_translation(self, key, **kwargs):
        """Get a translated string for the given key with optional formatting."""
        # Get the translation dictionary for the current language
        translations = self.translations.get(self.current_language, self.translations['en'])
        
        # Get the translated text or fallback to English or the key itself
        translated = translations.get(key)
        if translated is None:
            # Try English as fallback
            translated = self.translations['en'].get(key, key)
        
        # Apply any format parameters
        if kwargs and '{' in translated:
            try:
                translated = translated.format(**kwargs)
            except KeyError:
                # If formatting fails, return the unformatted string
                pass
                
        return translated
    
    def tr(self, key, **kwargs):
        """Shorthand method for get_translation."""
        return self.get_translation(key, **kwargs)
