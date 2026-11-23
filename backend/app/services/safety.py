SAFETY_GUIDANCE = {
    "before": {
        "title": "Before Your Trip",
        "description": "Prepare yourself and your vehicle before starting your journey.",
        "tips": [
            "Share your trip details and estimated arrival time with someone you trust.",
            "Verify the driver's name, vehicle number, and registration details.",
            "Check that the vehicle is in good condition.",
            "Keep your phone charged and carry emergency contact information.",
            "Confirm your pickup and drop-off locations before departure."
        ]
    },
    "during": {
        "title": "During Your Trip",
        "description": "Stay alert and take precautions throughout your journey.",
        "tips": [
            "Wear your seatbelt throughout the journey.",
            "Follow your route using a trusted map application.",
            "Avoid sharing unnecessary personal information.",
            "Keep your phone accessible in case of an emergency.",
            "If you feel unsafe, ask the driver to stop at a safe, public location.",
            "Share your live location with someone you trust."
        ]
    },
    "after": {
        "title": "After Your Trip",
        "description": "Make sure you have reached your destination safely.",
        "tips": [
            "Confirm your safe arrival with someone you trust.",
            "Check that you have all your belongings.",
            "Report any suspicious or unsafe behaviour.",
            "Provide feedback about your ride experience."
        ]
    }
}

EMERGENCY_CONTACTS = [
    {
        "name": "Police Emergency",
        "number": "15",
        "description": "For immediate police assistance."
    },
    {
        "name": "Rescue Service",
        "number": "1122",
        "description": "For medical emergencies, accidents, and rescue assistance."
    },
    {
        "name": "Motorway Police",
        "number": "130",
        "description": "For emergencies on national motorways and highways."
    }
]


def get_safety_guidance():
    return SAFETY_GUIDANCE


def get_emergency_contacts():
    return EMERGENCY_CONTACTS