import rtmidi2 as rtmidi
import time

from pymidi import server


# ------ récupère l'adresse ip dans ../ip.txt
chemin = __file__.split("/")
chemin = chemin[:-2]
chemin.append('ip.txt')

chemin = '/'.join(chemin)

print('ip récupérée de {}'.format(chemin))

adresseip = open(chemin).readlines()[0]
port = 5052

print('lancement...')

# ------ setup de la sortie midi
sortieMidi = rtmidi.MidiOut()


# ------ serviront à vérifier si une Teensy est branchée

sortieTeensy = '' # servira à stocker le nom de la sortie correspondant à la Teensy
foundTeensy = False


# ------ vérifie qu'une des sorties contient le nom "Teensy"
# ------ /!\ le script ne continuera pas tant qu'aucune Teensy n'est détectée

def verif_sorties(liste):
    global sortieTeensy

    for nom_sortie in liste:

        if 'Teensy' in nom_sortie:
            sortieTeensy = nom_sortie
            return True
    
    print('pas de teensy?')
    return False

while foundTeensy == False:
    sorties_disponibles = rtmidi.get_out_ports()
    foundTeensy = verif_sorties(sorties_disponibles)
    time.sleep(1)


print('\nTeensy trouvée!')

print('\nsortie MIDI: {}'.format(sortieTeensy))
sortieMidi.open_port(sortieTeensy)


print('\nenvoi de midi...')




# ------ séquence de démarrage, juste pour vérifier si ça marche     
# ------ le moteur doit faire un aller-retour complet en une 20aine de secondes

# print('position 0...')
sortieMidi.send_cc(0, 20, 127)    # vitesse max
sortieMidi.send_pitchbend(0, 0)   # position 0


time.sleep(7)  

print('on tourne !')
sortieMidi.send_pitchbend(0, 16383) # position max

time.sleep(7)

# --- demi-tour
print('demi-tour !')
sortieMidi.send_pitchbend(0, 0) # retour à la position 0

time.sleep(7)


# ------ permet de convertir un byte en int

def byte_to_int(byte):
    
    nouvelle_array = bytearray(byte)
    nombre_calcule = nouvelle_array[-1] * 128 + nouvelle_array[0]
    
    return nombre_calcule

# ------ la fonction qui sera lancée à la  réception de chaque message midi

def action(commande):

    for command in commande:

        # print(command.commande)

        # -- si la commande est un pitch bend

        if command.command_byte == 224 and command.channel != 7:
            valeur_pb = command.params.unknown
            # valeur_pb_convertie = int.from_bytes(valeur_pb, 'big')
            valeur_pb_convertie = byte_to_int(valeur_pb)

            print('! pitchbend @ {0} ({1})'.format(valeur_pb_convertie, valeur_pb))

            sortieMidi.send_pitchbend(0, valeur_pb_convertie)

        # -- si la commande est de type CC
        if command.command_byte == 176:

            index_cc = command.params.controller
            valeur_cc = command.params.value

            print('! cc{0} @ {1}'.format(index_cc, valeur_cc))

            sortieMidi.send_cc(0, index_cc, valeur_cc)



# ------ déclaration du serveur

class myHandler(server.Handler):
    
    # dès qu'une connexion est détectée
    def on_peer_connected(self, peer):
        print(':) connecté à {}'.format(peer))


    # indique si la connexion est perdue
    def on_peer_disconnected(self, peer):
        print(':( déconnecté de {}'.format(peer))

    
    def on_midi_commands(self, peer, command_list):
        # print(command_list)
        action(command_list)




print('démarrage du serveur sur {0}:{1}'.format(adresseip, port))

# ------ lancement du serveur

le_serveur = server.Server([(adresseip, port)])
le_serveur.add_handler(myHandler())
le_serveur.serve_forever()