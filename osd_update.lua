local msg = os.getenv("MSG_LOCK")
local mp = require 'mp'

-- Récupère le nom de l'utilisateur depuis l'environnement du système
local user = os.getenv("USER") or "Unknown"

-- Enregistre le moment de lancement de mpv
local start_time = os.time()

-- Fonction pour mettre à jour l'affichage
function update_osd()
    -- Calcule le temps écoulé en secondes, puis en minutes
    local elapsed_time = os.difftime(os.time(), start_time)
    local minutes_elapsed = math.floor(elapsed_time / 60)

    -- Génère le texte à afficher
    local text = string.format("%sLocked by %s \n %d minute%s ago",msg, user, minutes_elapsed, (minutes_elapsed == 1) and "" or "s")

    -- Affiche le texte avec OSD pendant 3 secondes
    mp.commandv("show-text", text, 3000)
end

-- Configure une mise à jour chaque minute
mp.add_periodic_timer(1, update_osd)
