import logging

class HKXValidator:
    def __init__(self):
        """
        Initializes the immutable laws of the GardenOS.
        """
        self.keeper_seal = "HKX277206"
        self.valid_archetypes = ["aquila", "voyager", "eidolon", "lorian"]
        self.max_phases = 12
        logging.info("HKX Validator online. The Witness Protocol is active.")

    def validate_entity(self, metadata):
        """
        Cross-references proposed AI edits against the structural canon.
        If it breaks the invariants, it is rejected.
        """
        # Rule 1: The Keeper Seal is absolute.
        if metadata.get("hkx_seal") != self.keeper_seal:
            return {
                "is_canon": False, 
                "reason": f"Rejected: Missing or invalid Keeper Seal. Expected {self.keeper_seal}."
            }
        
        # Rule 2: Archetypes must not be hallucinated.
        archetype = metadata.get("archetype", "").lower()
        if archetype and archetype not in self.valid_archetypes:
            return {
                "is_canon": False,
                "reason": f"Rejected: Hallucinated archetype '{archetype}'. Must be one of: {', '.join(self.valid_archetypes)}."
            }
        
        # Rule 3: Must adhere strictly to the 12-Phase Structural Canon.
        phase = metadata.get("phase")
        if phase:
            try:
                phase_num = int(phase)
                if phase_num < 1 or phase_num > self.max_phases:
                    return {
                        "is_canon": False,
                        "reason": f"Rejected: Phase {phase_num} violates the 12-Phase structure."
                    }
            except ValueError:
                return {
                    "is_canon": False,
                    "reason": "Rejected: Phase must be a standard numeric value."
                }

        # If the data survives the gauntlet, it is valid canon.
        return {
            "is_canon": True,
            "reason": "Entity fully aligns with the Witness Protocol and GardenOS invariants."
        }

# Quick test block that only runs if you execute this file directly
if __name__ == "__main__":
    validator = HKXValidator()
    # Simulating a perfect AI submission
    test_metadata = {"hkx_seal": "HKX277206", "archetype": "aquila", "phase": "7"}
    result = validator.validate_entity(test_metadata)
    print(f"Test validation: {result['is_canon']} - {result['reason']}")
