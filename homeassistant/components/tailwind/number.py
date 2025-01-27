"""Number entity platform for Tailwind."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from gotailwind import Tailwind, TailwindDeviceStatus

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TailwindDataUpdateCoordinator
from .entity import TailwindEntity


@dataclass(kw_only=True)
class TailwindNumberEntityDescription(NumberEntityDescription):
    """Class describing Tailwind number entities."""

    value_fn: Callable[[TailwindDeviceStatus], int]
    set_value_fn: Callable[[Tailwind, float], Awaitable[Any]]


DESCRIPTIONS = [
    TailwindNumberEntityDescription(
        key="brightness",
        icon="mdi:led-on",
        translation_key="brightness",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_min_value=0,
        native_max_value=100,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.led_brightness,
        set_value_fn=lambda tailwind, brightness: tailwind.status_led(
            brightness=int(brightness),
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tailwind number based on a config entry."""
    coordinator: TailwindDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TailwindNumberEntity(
            coordinator,
            description,
        )
        for description in DESCRIPTIONS
    )


class TailwindNumberEntity(TailwindEntity, NumberEntity):
    """Representation of a Tailwind number entity."""

    entity_description: TailwindNumberEntityDescription

    def __init__(
        self,
        coordinator: TailwindDataUpdateCoordinator,
        description: TailwindNumberEntityDescription,
    ) -> None:
        """Initiate Tailwind number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.device_id}-{description.key}"

    @property
    def native_value(self) -> int | None:
        """Return the number value."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Change to new number value."""
        await self.entity_description.set_value_fn(self.coordinator.tailwind, value)
        await self.coordinator.async_request_refresh()
