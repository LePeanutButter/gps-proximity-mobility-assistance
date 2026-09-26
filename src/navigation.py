"""Basic destination guidance for VisorSense."""

class NavigationManager:
    """Generate simple cardinal-direction guidance."""

    def __init__(self, destination_latitude, destination_longitude):
        self._destination_latitude = destination_latitude
        self._destination_longitude = destination_longitude

    def instruction(self, position):
        """Return a basic direction toward the configured destination."""
        if position is None:
            return "GPS WAIT"

        latitude_delta = self._destination_latitude - position.latitude
        longitude_delta = self._destination_longitude - position.longitude

        if abs(latitude_delta) < 0.0001 and abs(longitude_delta) < 0.0001:
            return "DESTINATION"

        if abs(latitude_delta) >= abs(longitude_delta):
            return "MOVE NORTH" if latitude_delta > 0 else "MOVE SOUTH"

        return "MOVE EAST" if longitude_delta > 0 else "MOVE WEST"
