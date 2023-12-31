import rtmidi2 as rtmidi
import time

from pymidi import server


# ------ récupère l'adresse ip dans ../ip.txt
chemin = __file__.split("/")
chemin = chemin[:-2]
chemin.append('ip.txt')

chemin = '/'.join(chemin)

print('ip récupérée de {}'.format(chemin))

adresseip = open(chemin).readlines()[0].split(' ')[0]

print(adresseip)
port = 5051

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

time.sleep(5)

print('\nsortie MIDI: {}'.format(sortieTeensy))
sortieMidi.open_port(sortieTeensy)


print('\nenvoi de midi...')



# ------ permet de convertir un byte en int

def byte_to_int(byte):
    
    nouvelle_array = bytearray(byte)
    nombre_calcule = nouvelle_array[-1] * 128 + nouvelle_array[0]
    
    return nombre_calcule







# ------ la fonction qui sera lancée à la  réception de chaque message midi

def action(commande):

    for command in commande:
        
        le_byte = command.command_byte

        # -- si la commande est un pitch bend

        if (le_byte > 223) and ((239 - le_byte) < 16):

            canal = command.channel

            valeur_pb = command.params.unknown

            valeur_pb_convertie = byte_to_int(valeur_pb)

            print('! pitchbend @ {0} ({1}), channel {2}'.format(valeur_pb_convertie, valeur_pb, canal))

            sortieMidi.send_pitchbend(canal, valeur_pb_convertie)

            return


        # -- peut-être pour renvoyer la position sur le channel 7?

        # if command.command_byte == 224 and command.channel == 7:
        #     sortieMidi.send_pitchbend(7, valeur_pb_convertie)

        # -- si la commande est de type CC
        if (le_byte > 175) and ((191 - le_byte) < 16):

            canal = command.channel

            index_cc = command.params.controller
            valeur_cc = command.params.value

            print('! cc{0} @ {1}, channel {2}'.format(index_cc, valeur_cc, canal))
            sortieMidi.send_cc(canal, index_cc, valeur_cc)

            return



# ------ classe de 'handler' qui sera utilisée pour lancer le serveur

class myHandler(server.Handler):

    # dès qu'une connexion est détectée
    def on_peer_connected(self, peer):
        
        global sortieMidi

        print(':) connecté à {}'.format(peer))
        

        # ------ montre qu'une connexion a bien eu lieu (bzz-bzz)
        # for i in range(16):
        #     sortieMidi.send_cc(i, 20, 127)
        #     sortieMidi.send_pitchbend(i, 100) # retour à la position 0
        
        # time.sleep(1.5)

        # for i in range(16):
        #     sortieMidi.send_pitchbend(i, 0) # retour à la position 0

        # time.sleep(1)


    # indique si la connexion est perdue
    def on_peer_disconnected(self, peer):
        
        global sortieMidi

        print(':( déconnecté de {}'.format(peer))

        
        # ------ montre qu'qu'une déconnexion a eu lieu (bzz-bzz-bzz)
        # for i in range(16):
        #     sortieMidi.send_cc(i, 20, 127)
        #     sortieMidi.send_pitchbend(i, 100)
        # time.sleep(1)
        # for i in range(16):
        #     sortieMidi.send_pitchbend(i, 200)
        # time.sleep(1)
        # for i in range(16):
        #     sortieMidi.send_pitchbend(i, 0)
        # time.sleep(1)

    
    def on_midi_commands(self, peer, command_list):

        action(command_list)



# ------ annonce à quelle adresse le serveur sera ouvert (si tout se passe bien, l'adresse de la carte + le port spécifié en haut du code)
print('démarrage du serveur sur {0}:{1}'.format(adresseip, port))

# ------ lancement du serveur

le_serveur = server.Server([(adresseip, port)])
le_serveur.add_handler(myHandler())
le_serveur.serve_forever()
