// Node-RED settings — Vibrocore V1
// Applied on WAGO PFC200 XTR (armv7, 512 MB RAM)

module.exports = {
    // Use single-file flow storage (no per-project overhead on 4 GB flash)
    flowFile: 'flows.json',
    flowFilePretty: true,

    // Dashboard title shown in browser tab
    ui: { path: 'ui', title: 'Vibrocore HMI' },

    // Editor — accessible from LAN only (not exposed externally)
    // For field use, disable the editor to save memory:
    //   disableEditor: true,
    editorTheme: {
        page: {
            title: 'Vibrocore V1',
        },
    },

    // Credentials encryption key (change before production deployment)
    credentialSecret: 'vibrocore-v1-secret',

    // Logging
    logging: {
        console: {
            level: 'info',
            metrics: false,
            audit: false,
        },
    },

    // Constrain Node-RED context storage to avoid flash wear
    contextStorage: {
        default: { module: 'memory' },
    },

    // Module allow-list (only what is needed)
    // The wagoautomation/node-red-iot image includes:
    //   node-red-dashboard, node-red-contrib-modbus, node-red-contrib-mqtt-broker
    externalModules: {
        autoInstall: false,
        palette: {
            allowInstall: true,
        },
    },
};
