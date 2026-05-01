import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository, DeviceTokenRepository
from app.modules.notifications.ports import PushNotificationPort
from app.modules.notifications.schemas import NotificationEventDTO, RegisterDeviceTokenDTO
from app.modules.notifications.models import NotificationType
from app.modules.notifications.exceptions import DuplicateDeviceTokenError


class TestNotificationServiceSendNotificationEvent:

    @pytest.fixture
    def notification_repo(self):
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture
    def push_adapter(self):
        return AsyncMock(spec=PushNotificationPort)

    @pytest.fixture
    def service(self, notification_repo, device_token_repo, push_adapter):
        return NotificationService(notification_repo, device_token_repo, push_adapter)

    @pytest.fixture
    def event_dto(self):
        return NotificationEventDTO(
            user_id=uuid4(),
            type=NotificationType.TRIP_STARTED,
            title="Trip Started",
            message="Your trip has begun"
        )
    
    @pytest.fixture
    def mock_notification(self):
        return MagicMock()

    @pytest.mark.asyncio
    async def test_send_notification_event_success(self, service, notification_repo, push_adapter, mock_notification, event_dto):
        """Test sending notification event successfully"""
        notification_repo.save.return_value = mock_notification
        push_adapter.send_to_user.return_value = True

        result = await service.send_notification_event(event_dto)

        assert result == mock_notification
        notification_repo.save.assert_called_once()
        push_adapter.send_to_user.assert_called_once()


class TestNotificationServiceGetUserNotifications:

    @pytest.fixture
    def notification_repo(self):
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture
    def push_adapter(self):
        return AsyncMock(spec=PushNotificationPort)

    @pytest.fixture
    def service(self, notification_repo, device_token_repo, push_adapter):
        return NotificationService(notification_repo, device_token_repo, push_adapter)

    @pytest.mark.asyncio
    async def test_get_user_notifications_empty(self, service, notification_repo):
        """Test getting user notifications when empty"""
        user_id = uuid4()
        notification_repo.get_user_notifications.return_value = []
        notification_repo.get_unread_count.return_value = 0

        result = await service.get_user_notifications(user_id)

        assert result.notifications == []
        assert result.unread_count == 0
        notification_repo.get_user_notifications.assert_called_once_with(user_id, 50, False)
        notification_repo.get_unread_count.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_with_data(self, service, notification_repo):
        """Test getting user notifications with data"""
        from app.modules.notifications.models import NotificationType, NotificationStatus
        from uuid import uuid4
        from datetime import datetime
        
        user_id = uuid4()
        # Create proper mock notifications with real values
        mock_notification = MagicMock()
        mock_notification.id = uuid4()
        mock_notification.type = NotificationType.TRIP_STARTED
        mock_notification.title = "Trip Started"
        mock_notification.message = "Your trip has begun"
        mock_notification.status = NotificationStatus.SENT
        mock_notification.trip_id = uuid4()
        mock_notification.created_at = datetime.now()
        mock_notification.read_at = None
        
        mock_notifications = [mock_notification]
        notification_repo.get_user_notifications.return_value = mock_notifications
        notification_repo.get_unread_count.return_value = 1

        result = await service.get_user_notifications(user_id)

        assert len(result.notifications) == 1
        assert result.unread_count == 1


class TestNotificationServiceRegisterDeviceToken:

    @pytest.fixture
    def notification_repo(self):
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture  
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture
    def push_adapter(self):
        return AsyncMock(spec=PushNotificationPort)

    @pytest.fixture
    def service(self, notification_repo, device_token_repo, push_adapter):
        return NotificationService(notification_repo, device_token_repo, push_adapter)

    @pytest.fixture
    def mock_device_token_obj(self):
        return MagicMock()

    @pytest.fixture
    def register_dto(self):
        return RegisterDeviceTokenDTO(
            device_token="ExponentPushToken[new-token]",
            device_type="ios"
        )

    @pytest.mark.asyncio
    async def test_register_device_token_new(self, service, device_token_repo, mock_device_token_obj, register_dto):
        """Test registering a new device token"""
        user_id = uuid4()
        device_token_repo.get_by_token.return_value = None 
        device_token_repo.register_device_token.return_value = mock_device_token_obj

        result = await service.register_device_token(user_id, register_dto)

        assert result == mock_device_token_obj
        device_token_repo.register_device_token.assert_called_once_with(
            user_id=user_id, device_token=register_dto.device_token, device_type=register_dto.device_type
        )

    @pytest.mark.asyncio
    async def test_register_device_token_duplicate_different_user(self, service, device_token_repo, mock_device_token_obj, register_dto):
        """Test registering a device token that exists for different user"""
        user_id = uuid4()
        different_user_id = uuid4() 
        mock_device_token_obj.is_active = True
        mock_device_token_obj.user_id = different_user_id
        device_token_repo.get_by_token.return_value = mock_device_token_obj

        with pytest.raises(DuplicateDeviceTokenError):
            await service.register_device_token(user_id, register_dto)

    @pytest.mark.asyncio
    async def test_register_device_token_reactivate_same_user(self, service, device_token_repo, mock_device_token_obj, register_dto):
        """Test reactivating device token for same user"""
        user_id = uuid4()
        mock_device_token_obj.is_active = False
        mock_device_token_obj.user_id = user_id
        device_token_repo.get_by_token.return_value = mock_device_token_obj
        device_token_repo.update.return_value = mock_device_token_obj

        result = await service.register_device_token(user_id, register_dto)

        assert result == mock_device_token_obj
        assert mock_device_token_obj.is_active is True
        device_token_repo.update.assert_called_once_with(mock_device_token_obj)


class TestNotificationServiceMarkNotificationsAsRead:

    @pytest.fixture
    def notification_repo(self):
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture
    def push_adapter(self):
        return AsyncMock(spec=PushNotificationPort)

    @pytest.fixture
    def service(self, notification_repo, device_token_repo, push_adapter):
        return NotificationService(notification_repo, device_token_repo, push_adapter)

    @pytest.mark.asyncio
    async def test_mark_notifications_as_read(self, service, notification_repo):
        """Test marking notifications as read"""
        user_id = uuid4()
        notification_ids = [uuid4(), uuid4()]
        notification_repo.mark_as_read.return_value = 2

        result = await service.mark_notifications_as_read(user_id, notification_ids)

        assert result == 2
        notification_repo.mark_as_read.assert_called_once_with(notification_ids, user_id)


class TestNotificationServiceHandleUserStoppedMovingEvent:

    @pytest.fixture
    def notification_repo(self):
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture
    def device_token_repo(self):
        return AsyncMock(spec=DeviceTokenRepository)

    @pytest.fixture
    def push_adapter(self):
        return AsyncMock(spec=PushNotificationPort)

    @pytest.fixture
    def service(self, notification_repo, device_token_repo, push_adapter):
        return NotificationService(notification_repo, device_token_repo, push_adapter)

    @pytest.mark.asyncio
    async def test_handle_user_stopped_moving_event(self, service):
        """Test handling user stopped moving event"""
        user_id = uuid4()
        trip_id = uuid4()

        with patch.object(service, 'send_notification_event') as mock_send:
            mock_send.return_value = MagicMock()

            await service.handle_user_stopped_moving_event(user_id, trip_id)

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args.user_id == user_id
            assert call_args.trip_id == trip_id
            assert call_args.type == NotificationType.TRIP_STOP_REMINDER