from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class CargoProfile:
    fragility: float
    label: str

    _KNOWN_LABELS: ClassVar[dict] = {2: "Low", 5: "Medium", 8: "High"}

    @classmethod
    def from_fragility(cls, fragility: float) -> "CargoProfile":
        label = cls._KNOWN_LABELS.get(fragility, str(fragility))
        return cls(fragility=fragility, label=label)
