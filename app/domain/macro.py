from pydantic import BaseModel, ConfigDict


class MacroData(BaseModel):
    """Macro economic snapshot."""

    model_config = ConfigDict(frozen=True)

    fed_rate: float | None = None

    us10y: float | None = None

    dxy: float | None = None

    vix: float | None = None

    inflation: float | None = None

    unemployment: float | None = None