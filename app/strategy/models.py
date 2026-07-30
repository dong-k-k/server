class StrategyRecommendation(Base):
    __tablename__ = "strategy_recommendation"
    recommendation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    settlement_id: Mapped[int] = mapped_column(ForeignKey("settlement_item.settlement_id"))
    match_id: Mapped[int] = mapped_column(ForeignKey("product_match_result.match_id"))
    risk_profile_id: Mapped[int] = mapped_column(ForeignKey("risk_profile.risk_profile_id"))
    recommendation_mix: Mapped[list] = mapped_column(JSON)
    recommendation_reason: Mapped[str | None] = mapped_column()
    pdf_url: Mapped[str | None] = mapped_column(String(300))