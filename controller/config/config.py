config = {
	"security": {
		"public_ca_key": "config/certchain.pem",
		"private_ca_key": "config/private.pem",
		"master_secret": "CliOmoacyieghoytsabwissEinfitbea"
	},
	"database": {
		"driver": "mysql",
		"username": "root",
		"password": "g7@#vgjaJl1",
        "host": "localhost",
        "port": 3306,
        "database": "HIP_VPLS"
	},
	"network": {
        "backlog": 200,
		"controller_port": 5010,
		"hostname": "hip-vpls-controller.strangebit.io" 
	},
	"general": {
		"buffer_size": 2000
	}
}
