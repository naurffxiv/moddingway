# Strikes constants
MINOR_INFRACTION_POINTS = 1
MODERATE_INFRACTION_POINTS = 3
SERIOUS_INFRACTION_POINTS = 7

# Strikes threshold and punisment array
THRESHOLDS_PUNISHMENT = [
    # Point threshold and punishment amount
    (10, 14),
    (7, 7),
    (5, 3),
    (3, 1),
]

AUTOMOD_INACTIVITY = {
    1273263026744590468: 30,  # lfg
    1273261496968810598: 30,  # lfm
    1240356145311252615: 30,  # temporary
    1301166606985990144: 7,  # scheduled pfs
}

STICKY_ROLES = [
    # Extra roles that should be removed from users when they are exiled
    # Right now there are no current roles that need to be removed other than verified
    # Verified is covered in the main method
]
