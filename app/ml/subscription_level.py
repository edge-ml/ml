from enum import Enum

class SubscriptionLevel(str, Enum):
    STANDARD = "standard"
    UPGRADED = "upgraded"
    UNLIMITED = "unlimited"

    @staticmethod
    def corresponding_timer(sub_level):
        if sub_level == SubscriptionLevel.STANDARD:
            return 20
        elif sub_level == SubscriptionLevel.UPGRADED:
            return 60
        elif sub_level == SubscriptionLevel.UNLIMITED:
            return None
        else:
            raise ValueError("Undefined subscription level")