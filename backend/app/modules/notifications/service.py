from typing import List, Optional
from uuid import UUID
import logging
from sqlalchemy import func
from app.modules.notifications.exceptions import InvalidNotificationDataError, NotificationNotFoundError, NotificationDeliveryError, DuplicateDeviceTokenError, NotificationPersistenceError
from app.modules.notifications.models import Notification, NotificationType, NotificationStatus, UserDeviceToken
from app.modules.notifications.ports import PushNotificationPort
from app.modules.notifications.repository import NotificationRepository, DeviceTokenRepository
from app.modules.notifications.schemas import NotificationEventDTO, NotificationListResponseDTO, NotificationResponseDTO, RegisterDeviceTokenDTO
from app.modules.trips.repository import TripRepo

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository, device_token_repo: DeviceTokenRepository, push_adapter: PushNotificationPort, trip_repo: TripRepo = None):
        self.notification_repo = notification_repo
        self.device_token_repo = device_token_repo
        self.push_adapter = push_adapter
        self.trip_repo = trip_repo
    
    async def send_notification_event(self, event: NotificationEventDTO) -> Notification:
        try:
            notification = Notification(
                user_id=event.user_id,
                type=event.type,
                title=event.title,
                message=event.message,
                trip_id=event.trip_id,
                status=NotificationStatus.PENDING
            )
            
            saved_notification = await self.notification_repo.save(notification)
            
            push_success = False
            try:
                push_success = await self.push_adapter.send_to_user(
                    user_id=event.user_id,
                    title=event.title,
                    message=event.message,
                    data={
                        "notification_id": str(saved_notification.id),
                        "type": event.type.value,
                        "trip_id": str(event.trip_id) if event.trip_id else None
                    }
                )
                
                await self.notification_repo.update_push_sent_status(saved_notification.id, push_success)
                
            except NotificationDeliveryError as e:
                logger.error(f"Failed to send push notification: {e}")
                await self.notification_repo.update_push_sent_status(saved_notification.id, False)
            except Exception as e:
                logger.error(f"Unexpected error sending push notification: {e}")
                await self.notification_repo.update_push_sent_status(saved_notification.id, False)
            
            if push_success:
                saved_notification.status = NotificationStatus.SENT
            else:
                saved_notification.status = NotificationStatus.FAILED

            saved_notification.push_sent = push_success
            
            return saved_notification
            
        except Exception as e:
            logger.error(f"Failed to process notification event: {e}")
            raise NotificationDeliveryError(f"Notification processing failed: {e}")
    
    async def get_user_notifications(self, user_id: UUID, limit: int = 50, unread_only: bool = False) -> NotificationListResponseDTO:
        try:
            notifications = await self.notification_repo.get_user_notifications(user_id, limit, unread_only)
            unread_count = await self.notification_repo.get_unread_count(user_id)
            
            return NotificationListResponseDTO(
                notifications=[NotificationResponseDTO.model_validate(n) for n in notifications],
                unread_count=unread_count
            )
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            raise NotificationNotFoundError(f"Failed to retrieve notifications: {e}")
    
    async def mark_notifications_as_read(self, user_id: UUID, notification_ids: List[UUID]) -> int:
        if not notification_ids:
            raise InvalidNotificationDataError("No notification IDs provided")
        
        try:
            return await self.notification_repo.mark_as_read(notification_ids, user_id)
        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {e}")
            raise NotificationPersistenceError(f"Failed to update notifications: {e}")
    
    async def register_device_token(self, user_id: UUID, device_data: RegisterDeviceTokenDTO) -> UserDeviceToken:
        if not device_data.device_token.strip():
            raise InvalidNotificationDataError("Device token cannot be empty")
        
        try:
            existing_token = await self.device_token_repo.get_by_token(device_data.device_token)
            
            if existing_token:
                if existing_token.user_id != user_id:
                    raise DuplicateDeviceTokenError("Device token is already registered to another user")
                
                existing_token.is_active = True
                existing_token.updated_at = func.now()
                return await self.device_token_repo.update(existing_token)
            
            return await self.device_token_repo.register_device_token(
                user_id=user_id, 
                device_token=device_data.device_token, 
                device_type=device_data.device_type
            )
        except DuplicateDeviceTokenError:
            raise
        except Exception as e:
            logger.error(f"Failed to register device token: {e}")
            raise NotificationPersistenceError(f"Device token registration failed: {e}")
    
    async def handle_user_stopped_moving_event(self, user_id: UUID, trip_id: Optional[UUID] = None):
        try:
            #getting active trip if the trip id isnt provided
            if not trip_id and self.trip_repo:
                active_trip = await self.trip_repo.get_active_trip(user_id)
                if active_trip:
                    trip_id = active_trip.id
            
            if not trip_id:
                logger.info(f"No active trip found for user {user_id}")
                return
            
            event = NotificationEventDTO(
                user_id=user_id,
                type=NotificationType.TRIP_STOP_REMINDER,
                title="Don't forget to stop your trip!",
                message="It looks like you've stopped moving. Don't forget to end your current trip to ensure accurate mileage tracking.",
                trip_id=trip_id
            )
            
            await self.send_notification_event(event)
            logger.info(f"Sent trip stop reminder to user {user_id} for trip {trip_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle user stopped moving event: {e}")
            raise
    
    async def handle_user_started_moving_event(self, user_id: UUID):
        try:
            #checking if user has an active trip fiorst before sending reminder
            if self.trip_repo:
                active_trip = await self.trip_repo.get_active_trip(user_id)
                if active_trip:
                    logger.info(f"User {user_id} already has active trip {active_trip.id}=")
                    return
            
            event = NotificationEventDTO(
                user_id=user_id,
                type=NotificationType.TRIP_START_REMINDER,
                title="Ready to track your trip?",
                message="It looks like you've started moving. Don't forget to start a new trip to track your mileage.",
                trip_id=None
            )
            
            await self.send_notification_event(event)
            logger.info(f"Sent trip start reminder to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle user started moving event: {e}")
            raise
    
    
    #this is for when scheduled trips are implemented
    #they arent implemented yet so these are very prone to change and currently dont work.
    
    async def notify_trip_started(self, user_id: UUID, trip_id: UUID, is_scheduled: bool = False):
        if not is_scheduled:
            return
        
        event = NotificationEventDTO(
            user_id=user_id,
            type=NotificationType.SCHEDULED_TRIP_STARTED,
            title="Scheduled Trip Started",
            message="Your scheduled trip has started. Safe travels!",
            trip_id=trip_id
        )
        
        await self.send_notification_event(event)
    
    async def notify_trip_ended(self, user_id: UUID, trip_id: UUID, is_scheduled: bool = False):
        if not is_scheduled:
            return
        
        event = NotificationEventDTO(
            user_id=user_id,
            type=NotificationType.SCHEDULED_TRIP_ENDED,
            title="Scheduled Trip Completed",
            message="Your scheduled trip has been completed successfully.",
            trip_id=trip_id
        )
        
        await self.send_notification_event(event)
