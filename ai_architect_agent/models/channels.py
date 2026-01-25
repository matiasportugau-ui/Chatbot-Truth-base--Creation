"""
Channel specifications for multi-channel chatbot deployment.

Based on official API documentation and real-world cost analysis for Uruguay market.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChannelType(Enum):
    """Supported communication channels."""
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"
    INSTAGRAM = "instagram"
    MERCADOLIBRE = "mercadolibre"


class IntegrationMethod(Enum):
    """How to integrate with the channel."""
    OFFICIAL_API = "official_api"
    BSP = "business_solution_provider"
    PLATFORM = "managed_platform"


@dataclass
class ChannelCost:
    """Cost structure for a channel."""
    monthly_base: float = 0.0  # Fixed monthly fee
    per_message_outbound: float = 0.0  # Cost per outbound message
    per_message_inbound: float = 0.0  # Cost per inbound message (usually 0)
    per_conversation: float = 0.0  # Per conversation (WhatsApp model)
    service_conversation_free: bool = False  # Customer-initiated free?
    notes: str = ""


@dataclass
class ChannelLimits:
    """Rate limits and restrictions."""
    messages_per_hour: Optional[int] = None
    messages_per_day: Optional[int] = None
    response_window_hours: int = 24  # Time to respond before restrictions
    max_message_length: Optional[int] = None
    requires_user_initiation: bool = False


@dataclass
class ChannelRequirements:
    """Requirements for channel setup."""
    business_verification: bool = False
    app_review_required: bool = False
    webhook_https: bool = True
    oauth_required: bool = False
    estimated_setup_days: int = 1
    technical_complexity: int = 5  # 1-10 scale


@dataclass
class ChannelConfig:
    """Base configuration for any channel."""
    channel_type: ChannelType
    enabled: bool = True
    priority: int = 1  # Higher = more important
    integration_method: IntegrationMethod = IntegrationMethod.OFFICIAL_API
    cost: ChannelCost = field(default_factory=ChannelCost)
    limits: ChannelLimits = field(default_factory=ChannelLimits)
    requirements: ChannelRequirements = field(default_factory=ChannelRequirements)


@dataclass
class WhatsAppConfig(ChannelConfig):
    """
    WhatsApp Business Cloud API configuration.

    Key insight: Service conversations (customer-initiated) are FREE since Nov 2024.
    Most quotation inquiries are customer-initiated, making this highly cost-effective.

    Pricing for Uruguay (Rest of Latin America):
    - Marketing messages: ~$0.065/message
    - Utility messages: ~$0.012/message
    - Service conversations: FREE (24-hour window)
    """

    def __init__(self):
        super().__init__(
            channel_type=ChannelType.WHATSAPP,
            priority=1,  # Highest priority - handles 70%+ of traffic
            integration_method=IntegrationMethod.OFFICIAL_API,
            cost=ChannelCost(
                monthly_base=0.0,  # No base fee with Cloud API
                per_conversation=0.0,  # Service conversations free
                per_message_outbound=0.012,  # Utility rate (conservative)
                service_conversation_free=True,
                notes="Meta Cloud API direct. Marketing=$0.065, Utility=$0.012. "
                      "Service conversations (customer-initiated) FREE since Nov 2024."
            ),
            limits=ChannelLimits(
                messages_per_day=1000,  # Starter tier
                response_window_hours=24,
                max_message_length=4096,
            ),
            requirements=ChannelRequirements(
                business_verification=True,
                webhook_https=True,
                estimated_setup_days=14,  # 1-3 weeks including verification
                technical_complexity=8,
            )
        )
        self.phone_number_id: Optional[str] = None
        self.business_account_id: Optional[str] = None
        self.access_token: Optional[str] = None
        self.verify_token: Optional[str] = None
        self.webhook_url: Optional[str] = None


@dataclass
class MessengerConfig(ChannelConfig):
    """
    Facebook Messenger configuration via Graph API.

    Key insight: Completely FREE - no per-message or subscription costs.
    Same Facebook App can handle both Messenger and Instagram.
    """

    def __init__(self):
        super().__init__(
            channel_type=ChannelType.MESSENGER,
            priority=2,
            integration_method=IntegrationMethod.OFFICIAL_API,
            cost=ChannelCost(
                monthly_base=0.0,
                per_message_outbound=0.0,
                per_message_inbound=0.0,
                notes="Graph API is completely FREE. No message fees."
            ),
            limits=ChannelLimits(
                response_window_hours=24,
                max_message_length=2000,
            ),
            requirements=ChannelRequirements(
                business_verification=False,
                app_review_required=True,  # pages_messaging permission
                webhook_https=True,
                estimated_setup_days=10,  # App review can take up to 10 days
                technical_complexity=6,
            )
        )
        self.page_id: Optional[str] = None
        self.page_access_token: Optional[str] = None
        self.app_id: Optional[str] = None
        self.app_secret: Optional[str] = None


@dataclass
class InstagramConfig(ChannelConfig):
    """
    Instagram Direct Messages configuration via Graph API.

    Key insight: FREE but user must message first (can't initiate).
    200 DMs/hour rate limit. Shares Facebook App with Messenger.
    """

    def __init__(self):
        super().__init__(
            channel_type=ChannelType.INSTAGRAM,
            priority=3,
            integration_method=IntegrationMethod.OFFICIAL_API,
            cost=ChannelCost(
                monthly_base=0.0,
                per_message_outbound=0.0,
                per_message_inbound=0.0,
                notes="Graph API is completely FREE. Same app as Messenger."
            ),
            limits=ChannelLimits(
                messages_per_hour=200,
                response_window_hours=24,
                requires_user_initiation=True,  # Cannot message first
            ),
            requirements=ChannelRequirements(
                business_verification=False,
                app_review_required=True,
                webhook_https=True,
                estimated_setup_days=10,
                technical_complexity=6,
            )
        )
        self.instagram_account_id: Optional[str] = None
        self.connected_page_id: Optional[str] = None  # Must be linked to FB Page


@dataclass
class MercadoLibreConfig(ChannelConfig):
    """
    Mercado Libre Questions & Messages API configuration.

    Key insights:
    - FREE for registered sellers
    - Two systems: Questions API (pre-sale) and Messages API (post-sale)
    - 350-character limit for post-sale messages
    - OAuth tokens expire every 6 hours (refresh tokens last 6 months)
    - Messages flagged as AUTOMATIC_MESSAGE may be moderated
    """

    def __init__(self):
        super().__init__(
            channel_type=ChannelType.MERCADOLIBRE,
            priority=2,  # High priority for e-commerce
            integration_method=IntegrationMethod.OFFICIAL_API,
            cost=ChannelCost(
                monthly_base=0.0,
                per_message_outbound=0.0,
                per_message_inbound=0.0,
                notes="FREE for registered sellers. Focus on Questions API for pre-sale."
            ),
            limits=ChannelLimits(
                max_message_length=350,  # Post-sale limit
                response_window_hours=48,  # Questions expire after 48h
            ),
            requirements=ChannelRequirements(
                business_verification=False,  # Just need seller account
                app_review_required=False,  # But certification recommended
                webhook_https=True,
                oauth_required=True,
                estimated_setup_days=14,  # 2-3 weeks for full implementation
                technical_complexity=7,
            )
        )
        self.seller_id: Optional[str] = None
        self.app_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.site_id: str = "MLU"  # Uruguay


@dataclass
class Channel:
    """Complete channel specification with all metadata."""
    config: ChannelConfig
    name: str
    description: str
    typical_traffic_share: float  # Percentage of total traffic (0-1)
    implementation_hours: int  # Estimated dev hours
    maintenance_hours_monthly: int

    @classmethod
    def whatsapp(cls) -> "Channel":
        return cls(
            config=WhatsAppConfig(),
            name="WhatsApp Business",
            description="Primary channel for direct customer communication. "
                        "Handles quotation requests, order updates, and support.",
            typical_traffic_share=0.70,
            implementation_hours=40,
            maintenance_hours_monthly=4,
        )

    @classmethod
    def messenger(cls) -> "Channel":
        return cls(
            config=MessengerConfig(),
            name="Facebook Messenger",
            description="Secondary channel for customers discovering via Facebook. "
                        "Often used for initial inquiries before moving to WhatsApp.",
            typical_traffic_share=0.15,
            implementation_hours=16,
            maintenance_hours_monthly=2,
        )

    @classmethod
    def instagram(cls) -> "Channel":
        return cls(
            config=InstagramConfig(),
            name="Instagram DMs",
            description="Visual-first channel for younger demographics. "
                        "Product inquiries driven by posts/stories.",
            typical_traffic_share=0.10,
            implementation_hours=8,  # Shares codebase with Messenger
            maintenance_hours_monthly=2,
        )

    @classmethod
    def mercadolibre(cls) -> "Channel":
        return cls(
            config=MercadoLibreConfig(),
            name="Mercado Libre",
            description="E-commerce marketplace integration. "
                        "Pre-sale questions drive conversion; post-sale for order support.",
            typical_traffic_share=0.05,
            implementation_hours=60,  # More complex integration
            maintenance_hours_monthly=4,
        )

    @classmethod
    def all_channels(cls) -> list["Channel"]:
        """Get all supported channels in priority order."""
        return [
            cls.whatsapp(),
            cls.messenger(),
            cls.instagram(),
            cls.mercadolibre(),
        ]


def estimate_channel_costs(
    channel: Channel,
    monthly_conversations: int,
    customer_initiated_ratio: float = 0.70,
) -> dict:
    """
    Estimate monthly costs for a channel.

    Args:
        channel: Channel configuration
        monthly_conversations: Expected monthly conversation volume
        customer_initiated_ratio: Percentage of conversations started by customer

    Returns:
        Dict with cost breakdown
    """
    config = channel.config
    cost = config.cost

    # Base cost
    total = cost.monthly_base

    # Calculate message costs
    if config.channel_type == ChannelType.WHATSAPP:
        # WhatsApp: service conversations free, only pay for business-initiated
        business_initiated = monthly_conversations * (1 - customer_initiated_ratio)
        # Assume 50% marketing, 50% utility for business-initiated
        marketing_msgs = business_initiated * 0.5
        utility_msgs = business_initiated * 0.5
        message_cost = (marketing_msgs * 0.065) + (utility_msgs * 0.012)
        total += message_cost
    else:
        # Other channels: typically free or per-message
        messages_per_conversation = 5  # Average
        total_messages = monthly_conversations * messages_per_conversation
        total += total_messages * cost.per_message_outbound

    return {
        "channel": channel.name,
        "monthly_base": cost.monthly_base,
        "message_costs": total - cost.monthly_base,
        "total_monthly": round(total, 2),
        "cost_per_conversation": round(total / max(monthly_conversations, 1), 4),
        "notes": cost.notes,
    }
