module.exports = {
    networks: {
        development: {
            host: '127.0.0.1',
            port: 8545,
            network_id: '*',
        },
        polygon: {
            provider: () => new HDWalletProvider(mnemonic, `https://polygon-rpc.com`),
            network_id: 137,
            gas: 5500000,
            confirmations: 2,
            timeoutBlocks: 200,
        },
    },
    compilers: {
        solc: {
            version: '0.8.0',
            settings: { optimizer: { enabled: true, runs: 200 } },
        },
    },
};
