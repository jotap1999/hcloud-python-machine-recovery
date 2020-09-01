from hcloud import Client
from hcloud.images.domain import Image
from hcloud.server_types.domain import ServerType
from hcloud.servers.domain import Server


client = Client(token="......")
serverName = "test" 


oldServer = client.servers.get_by_name(name=serverName)

#Shut down the OldServer
try:
    oldServer.power_off()
except:
    print("Error when turning down the server. Confirm if the server's name is right")
    quit()


#Get all the information of the old server
oldServerType = (Server(id=oldServer).id).server_type
oldServerDatacenter = (Server(id=oldServer).id).datacenter
oldServerVolumes = (Server(id=oldServer).id).volumes
oldServerFloatingIP = ((Server(id=oldServer).id).public_net).floating_ips

sshKeys = client.ssh_keys.get_all()

#Find the newest backup
images = client.images.get_all(type="backup")
backupNewestID = 0
for image in images:
    infImage = (client.images.get_by_id(image.id))
    createdFrom = ((Image(id=infImage).id).created_from).name
    if createdFrom == serverName:
        idImage = infImage.id
        if idImage > backupNewestID:
            backupNewestID = idImage
imageNewServer = client.images.get_by_id(backupNewestID)


#detach Volume, unassign IP  and change name
for x in range(len(oldServerVolumes)):
    oldServerVolumes[x].detach()
client.floating_ips.unassign((oldServerFloatingIP)[0])
try:
    oldServer.update(name=serverName + "-OLD")
except:
    x = 1
    while True:
        oldServerTry = client.servers.get_by_name(name=serverName + "-OLD." + str(x))
        if oldServerTry is None:
            oldServer.update(name=serverName + "-OLD." + str(x))
            break
        x += 1 


#create machine
try:
    create_action = client.servers.create(
        name=serverName,
        server_type=oldServerType,
        image=imageNewServer,
        datacenter=oldServerDatacenter,
        ssh_keys=sshKeys,
        volumes=oldServerVolumes
    )
    newServer = create_action.server
    client.floating_ips.assign((oldServerFloatingIP)[0], newServer)
    newServer.enable_backup()
except:
    print("Error when creating the server.")
    quit()



