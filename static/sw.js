self.addEventListener('fetch', event => {
    if (event.request.method !== 'POST') return;
    if (event.request.url.indexOf('/app') === -1) return;

    // /* This is to fix the issue Jake found */
    // event.respondWith(Response.redirect('/'));

    event.waitUntil(async () => {
        const data = await event.request.formData();
        // Get the data from the named element 'file'
        return fetch("/app_share", {
            method: "POST",
            body: data,
            headers: {
                "Content-Type": "multipart/form-data"
            }
        })
    });
});
