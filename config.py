BOT_CONFIG = {
    "window_title": "AlcazarMeta",
    "region": None,
    "detection": {
        "template_paths": [
            "stone_template_1.png",
            "stone_template_2.png",
            "stone_template_3.png",
        ],
        "min_confidence": 0.70,
        "min_scale": 0.50,
        "max_scale": 1.60,
        "scale_step": 0.05,
        "min_distance": 80,
        "max_detections": 10,
    },
    "targeting": {
        "enabled": True,
        "click_delay": 0.60,
        "rescan_delay": 1.00,
        "center_bias": 0.15,
    },
}
