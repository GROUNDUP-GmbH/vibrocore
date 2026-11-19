// Node-RED settings — Vibrocore V1
// Applied on WAGO PFC200 XTR (armv7, 512 MB RAM)
//
// Secrets (never commit real values):
//   NODE_RED_CREDENTIAL_SECRET  — encrypts credentials in flows
//   NODE_RED_USERNAME           — editor login (default: admin)
//   NODE_RED_PASSWORD_HASH      — bcrypt hash of the editor password
//   NODE_RED_PASSWORD_HASH_FILE — alternative: path to a file that holds the hash
//
// Generate a hash on a trusted host:
//   node -e "console.log(require('bcryptjs').hashSync(process.argv[1], 8))" 'YOUR_PASSWORD'

'use strict';

const fs = require('fs');

function readSecret(envValue, fileEnv) {
    if (envValue && String(envValue).trim() !== '') {
        return String(envValue).trim();
    }
    const filePath = process.env[fileEnv];
    if (filePath) {
        return fs.readFileSync(filePath, 'utf8').trim();
    }
    return '';
}

const credentialSecret = readSecret(
    process.env.NODE_RED_CREDENTIAL_SECRET,
    'NODE_RED_CREDENTIAL_SECRET_FILE'
);
if (!credentialSecret) {
    throw new Error(
        'NODE_RED_CREDENTIAL_SECRET (or NODE_RED_CREDENTIAL_SECRET_FILE) must be set'
    );
}

const passwordHash = readSecret(
    process.env.NODE_RED_PASSWORD_HASH,
    'NODE_RED_PASSWORD_HASH_FILE'
);
if (!passwordHash) {
    throw new Error(
        'NODE_RED_PASSWORD_HASH (or NODE_RED_PASSWORD_HASH_FILE) must be set — no default password'
    );
}

const adminUser = process.env.NODE_RED_USERNAME || 'admin';

module.exports = {
    // Use single-file flow storage (no per-project overhead on 4 GB flash)
    flowFile: 'flows.json',
    flowFilePretty: true,

    // Dashboard title shown in browser tab
    ui: { path: 'ui', title: 'Vibrocore HMI' },

    // Editor — require login; bind at compose level to 127.0.0.1 / HMI LAN only
    adminAuth: {
        type: 'credentials',
        users: [
            {
                username: adminUser,
                password: passwordHash,
                permissions: '*',
            },
        ],
    },

    editorTheme: {
        page: {
            title: 'Vibrocore V1',
        },
    },

    // Credentials encryption key from environment / secret file (no hard-coded secret)
    credentialSecret: credentialSecret,

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

    // Module allow-list — field units must not install palette packages
    // The wagoautomation/node-red-iot image includes:
    //   node-red-dashboard, node-red-contrib-modbus, node-red-contrib-mqtt-broker
    externalModules: {
        autoInstall: false,
        palette: {
            allowInstall: false,
        },
    },
};
