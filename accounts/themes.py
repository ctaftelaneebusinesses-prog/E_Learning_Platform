"""Theme registry mapping Profile.education_type to visual identity metadata.

Each entry drives the `body.theme-*` CSS class (see static/css/themes.css),
the greeting copy on the student dashboard, and the placeholder illustration
slots under static/images/themes/<key>/.
"""

THEME_CONFIG = {
    'SCHOOL': {
        'key': 'school',
        'css_class': 'theme-school',
        'label': 'School (Classes 1-10)',
        'greeting': 'Good Morning, Superstar!',
        'tagline': "Ready for today's magical learning adventure?",
        'heading_font': None,
        'heading_font_family': "'Baloo 2', var(--font-sans)",
        'banner_illustration': 'images/themes/school/banner.svg',
        'badge_illustration': 'images/themes/school/badge.svg',
        'empty_state_illustration': 'images/themes/school/empty-state.svg',
        'mascot_illustration': 'images/themes/school/mascot.svg',
        'icon': 'bi-stars',
        # Kids World extras — see static/css/kids-theme.css + static/js/kids-*.js
        'is_kids_world': True,
        'has_animated_scene': True,
        'sounds': {
            'click': 'audio/kids/click.wav',
            'reward': 'audio/kids/reward.wav',
            'achievement': 'audio/kids/achievement.wav',
            'celebration': 'audio/kids/celebration.wav',
        },
    },
    'INTERMEDIATE': {
        'key': 'intermediate',
        'css_class': 'theme-intermediate',
        'label': 'Intermediate (11-12)',
        'greeting': 'Welcome back,',
        'tagline': 'Keep building on your progress.',
        'heading_font': None,
        'heading_font_family': "var(--font-sans)",
        'banner_illustration': 'images/themes/intermediate/banner.svg',
        'badge_illustration': 'images/themes/intermediate/badge.svg',
        'empty_state_illustration': 'images/themes/intermediate/empty-state.svg',
        'icon': 'bi-mortarboard',
        'has_animated_scene': True,
    },
    'COLLEGE': {
        'key': 'college',
        'css_class': 'theme-college',
        'label': 'College',
        'greeting': 'Welcome back,',
        'tagline': "Let's keep shipping progress.",
        'heading_font': None,
        'heading_font_family': "var(--font-sans)",
        'banner_illustration': 'images/themes/college/banner.svg',
        'badge_illustration': 'images/themes/college/badge.svg',
        'empty_state_illustration': 'images/themes/college/empty-state.svg',
        'icon': 'bi-code-slash',
    },
    'UNIVERSITY': {
        'key': 'university',
        'css_class': 'theme-university',
        'label': 'University',
        'greeting': 'Welcome back,',
        'tagline': 'Continue your research and studies.',
        'heading_font': "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap",
        'heading_font_family': "'Playfair Display', var(--font-sans)",
        'banner_illustration': 'images/themes/university/banner.svg',
        'badge_illustration': 'images/themes/university/badge.svg',
        'empty_state_illustration': 'images/themes/university/empty-state.svg',
        'icon': 'bi-bank',
    },
    'OTHER': {
        'key': 'other',
        'css_class': 'theme-other',
        'label': 'Other',
        'greeting': 'Welcome back,',
        'tagline': 'Keep growing your skills.',
        'heading_font': None,
        'heading_font_family': "var(--font-sans)",
        'banner_illustration': 'images/themes/other/banner.svg',
        'badge_illustration': 'images/themes/other/badge.svg',
        'empty_state_illustration': 'images/themes/other/empty-state.svg',
        'icon': 'bi-briefcase',
    },
}

# School theme is the only one that needs a non-default webfont.
THEME_CONFIG['SCHOOL']['heading_font'] = (
    "https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&display=swap"
)


def get_theme(education_type):
    """Return the theme dict for a Profile.education_type value.

    Blank / unknown / non-student values fall back to the neutral 'OTHER' theme.
    """
    return THEME_CONFIG.get(education_type) or THEME_CONFIG['OTHER']
