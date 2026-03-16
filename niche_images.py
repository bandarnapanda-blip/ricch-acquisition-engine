# niche_images.py
# Curated Unsplash image IDs for all 11 niches.
# Each niche has a hero, team, and background image.
# Fallbacks are hardcoded so generation never stops if Unsplash is down.

NICHE_IMAGES = {
    "Solar Energy Installers": {
        "hero":       "https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1497440001374-f26997328c1b?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1605980776566-0486c3ac7617?w=1800&q=85",
    },
    "Personal Injury Attorneys": {
        "hero":       "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=1200&q=85",
        "team":       "https://images.unsplash.com/photo-1556157382-97eda2d62296?w=800&q=80",
        "background": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1800&q=85",
    },
    "Luxury Home Remodeling": {
        "hero":       "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1400&q=80",
        "background": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1800&q=85",
    },
    "HVAC and Climate Control": {
        "hero":       "https://images.unsplash.com/photo-1504222490345-c075b7c1cba6?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=1800&q=85",
    },
    "Dental Implant Specialists": {
        "hero":       "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1200&q=85",
        "team":       "https://images.unsplash.com/photo-1588776814546-1ffedde4d2d3?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?w=1800&q=85",
    },
    "Epoxy Garage Flooring": {
        "hero":       "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=1800&q=85",
    },
    "Roofing Contractors": {
        "hero":       "https://images.unsplash.com/photo-1632889822533-e9b7c4a35b3c?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1591588582259-e675cb2dbf1a?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?w=1800&q=85",
    },
    "Concrete and Paving": {
        "hero":       "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1513828583688-c52646db42da?w=1800&q=85",
    },
    "Landscaping Design": {
        "hero":       "https://images.unsplash.com/photo-1558904541-efa843a96f01?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=85",
        "background": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1600240644455-3edc55c375fe?w=1800&q=85",
    },
    "Pool and Spa Builders": {
        "hero":       "https://images.unsplash.com/photo-1575429198097-0414ec08e8cd?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1400&q=80",
        "background": "https://images.unsplash.com/photo-1562778612-e1e0cda9915c?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1800&q=85",
    },
    "Kitchen and Bath Remodelers": {
        "hero":       "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1800&q=85",
        "team":       "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1400&q=80",
        "background": "https://images.unsplash.com/photo-1600489000022-c2086d79f9d4?w=1800&q=85",
        "fallback":   "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=1800&q=85",
    },
}


def get_images(niche: str) -> dict:
    """
    Get image URLs for a given niche.
    Falls back to a safe generic set if niche not found.
    """
    images = NICHE_IMAGES.get(niche)

    if not images:
        # Generic premium fallback
        return {
            "hero":       "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1800&q=85",
            "team":       "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1400&q=80",
            "background": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1800&q=85",
            "fallback":   "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1800&q=85",
        }

    return images


def get_hero_image(niche: str) -> str:
    """Shortcut to get just the hero image URL."""
    return get_images(niche)["hero"]


def get_team_image(niche: str) -> str:
    """Shortcut to get just the team image URL."""
    return get_images(niche)["team"]


def get_background_image(niche: str) -> str:
    """Shortcut to get just the background image URL."""
    return get_images(niche)["background"]


def get_fallback_image(niche: str) -> str:
    """Shortcut to get the fallback image URL."""
    return get_images(niche)["fallback"]
