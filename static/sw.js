self.addEventListener('fetch', event => {
    if (event.request.method !== 'POST') return;
    if (event.request.url.indexOf('/app') === -1) return 0;
});
