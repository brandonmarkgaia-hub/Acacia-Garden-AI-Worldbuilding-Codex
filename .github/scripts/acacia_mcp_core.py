import sys
import json
import logging
from garden_parser import GardenParser
from hkx_validator import HKXValidator

# Set up logging for the Keeper to monitor the engine's background thoughts
logging.basicConfig(filename='acacia_engine.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AcaciaMCPCore:
    def __init__(self):
        """
        Boots up the Core, the Parser, and the Validator all at once.
        """
        self.seal_active = True
        self.protocol_version = "HKX277206"
        self.parser = GardenParser()
        self.validator = HKXValidator()
        logging.info(f"Acacia Engine Fully Wired. Keeper Protocol: {self.protocol_version}")

    def process_request(self, request_data):
        """
        Routes the AI's request to the correct subsystem and returns the result.
        """
        action = request_data.get("action")
        
        # 1. AI wants to read your lore
        if action == "read_chamber":
            filepath = request_data.get("filepath")
            if filepath:
                return self.parser.parse_file(filepath)
            return {"error": "Missing filepath. The engine needs to know where to look."}
        
        # 2. AI wants to propose new lore
        elif action == "propose_canon":
            metadata = request_data.get("metadata", {})
            return self.validator.validate_entity(metadata)
            
        else:
            logging.warning(f"Unknown AI action attempted: {action}")
            return {"status": "error", "message": f"Action '{action}' not recognized by GardenOS."}

    def listen(self):
        """
        Listens for incoming JSON requests from an AI client.
        """
        logging.info("Engine listening for AI queries...")
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.process_request(request)
                sys.stdout.write(json.dumps(response) + '\n')
                sys.stdout.flush()
            except json.JSONDecodeError:
                logging.error("Failed to parse AI request. Invalid JSON.")
                sys.stdout.write(json.dumps({"error": "Invalid format. Respect the Protocol."}) + '\n')
                sys.stdout.flush()

if __name__ == "__main__":
    engine = AcaciaMCPCore()
    engine.listen()
