from pydantic import BaseModel

class ChurnInput(BaseModel):
    MonthlyRevenue: float
    MonthlyMinutes: float
    OverageMinutes: float
    UnansweredCalls: int
    CustomerCareCalls: int
    PercChangeMinutes: float
    PercChangeRevenues: float
    InboundCalls: int
    OutboundCalls: int
    ReceivedCalls: int
    TotalRecurringCharge: float
    CurrentEquipmentDays: int
    DroppedBlockedCalls: int
    MonthsInService: int
    ActiveSubs: int
    RespondsToMailOffers: str
    RetentionCalls: int
    RetentionOffersAccepted: int
    MadeCallToRetentionTeam: str
    ReferralsMadeBySubscriber: int
    CreditRating: str
    IncomeGroup: str
    Occupation: str
    PrizmCode: str
