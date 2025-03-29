import asyncio
import inspect
from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from simple_logger.logger import get_logger, SimpleLogger


logger: SimpleLogger = get_logger("configuration")
class RedisListener:
    def __init__(self, redis_url: str, channels: dict):
        """
        Initialiser le listener Redis.

        Args:
            redis_client (Redis): Instance Redis connectée.
            channels (dict): Dictionnaire des canaux Redis et des callbacks associés.
        """
        self.channels = channels  # {channel_name: callback_function}
        self.redis_client = Redis.from_url(redis_url, decode_responses=True)
        self.pubsub = None  # Store the pubsub object here
        self.listener_task = None
        self._stop_event = asyncio.Event()
        self.running = False  # État du listener

    async def start(self):
        """
        Start Redis Listener for all specified channels.
        """
        if self.running:
            raise RuntimeError("RedisListener is already running. Stop it before starting again.")

        try:
            self.pubsub = self.redis_client.pubsub() # Initialize pubsub here
            # Subscribe to channels
            for channel in self.channels.keys():
                try:
                    await self.pubsub.subscribe(channel)
                    await logger.ainfo(f"Subscribed to channel: {channel}")
                except Exception as e:
                    await logger.acritical(f"Error subscribing to channel {channel}: {e}")
                    raise

            self.running = True
            self.listener_task = asyncio.create_task(self._listen()) # No need to pass pubsub
            await logger.ainfo("Redis listener successfully started.")

        except Exception as e:
            await logger.acritical(f"Failed to subscribe or listen to Redis channels: {e}")
            if self.pubsub:
                await self.pubsub.close()
            self.pubsub = None
            raise

    async def _listen(self):
        try:
            await logger.ainfo("Redis listener started.")
            async for message in self.pubsub.listen(): # Use async for
                if message["type"] == "message":
                    channel = message["channel"].decode("utf-8")
                    data = message["data"].decode("utf-8")
                    await self._handle_message(channel, data)

        except asyncio.CancelledError:
            await logger.aerror("Redis listener stopped gracefully due to cancellation.")
        except Exception as e:
            await logger.aerror(f"Redis listener encountered an error: {e}")
        finally:
            self.running = False
            if self.pubsub:
                await self.pubsub.close()
                self.pubsub = None # Important: set to None after closing
            await logger.ainfo("Redis listener stopped gracefully.")

    async def _handle_message(self, channel, data):
        """
        Handle received message based on the channel.
        """
        if channel in self.channels:
            callback = self.channels[channel]
            await logger.ainfo(f"Received message on channel {channel}: {data}")
            # Vérifie si le callback est asynchrone
            if inspect.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        else:
            await logger.awarning(f"Unhandled channel: {channel} - Message: {data}")

    async def stop(self):
        """
        Arrêter le listener Redis.

        Raises:
            RuntimeError: Si le listener n'est pas en cours d'exécution.
        """
        if not self.running:
            raise RuntimeError("RedisListener is not running. Cannot stop a non-running listener.")

        self._stop_event.set()
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                await logger.awarning("Redis listener was already stopped due to cancellation.")
        if self.pubsub:
            await self.pubsub.close()
            self.pubsub = None
        if self.redis_client:
            await self.redis_client.close()

        self.running = False
        await logger.ainfo("Redis listener stopped and Redis client closed.")
