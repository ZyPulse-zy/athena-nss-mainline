// Keep the algorithms actually negotiated by the failing default connections.
// Apply only to owned fixture/control processes; never edit global SSH policy.
export const compactSshOptions=Object.freeze([
  '-o','KexAlgorithms=curve25519-sha256',
  '-o','Ciphers=chacha20-poly1305@openssh.com',
  '-o','HostKeyAlgorithms=ssh-ed25519',
  '-o','MACs=hmac-sha2-256-etm@openssh.com',
  '-o','Compression=no',
]);
