from pytune_configuration.config_service import Config

class ConfigChangeHandler:
    def __init__(self, config:Config):
        """
        Initialiser le gestionnaire de changements de configuration.

        Args:
            config (Config): Instance de configuration à gérer.
        """
        self.config = config

    async def handle_message(self, message):
        """
        Gérer un message reçu depuis Redis.

        Args:
            message (str): Le message reçu.
        """
        try:
            if message.startswith("config_update:"):
                _, config_data = message.split("config_update:")
                key, value = config_data.split(":", 1)
                await self.config.update_config(key, value)
            elif message.startswith("config_delete:"):
                _, key = message.split("config_delete:")
                await self.config.delete_config(key)
            elif message.startswith("config_add:"):
                _, config_data = message.split("config_add:")
                key, value = config_data.split(":", 1)
                await self.config.add_config(key, value)
            elif message == "force_reload":
                await self.config.reload_configurations()
            else:
                await self.config.logger.log_warning(f"Unrecognized message received: {message}")
        except Exception as e:
            await self.config.logger.log_critical(f"Error handling config change message: {e}")
