fetch('people.json')
.then(response => response.json())
.then(data => {

    const params = new URLSearchParams(window.location.search);
    const id = params.get("id") || "jared";

    const person = data[id];

    if (!person) {
        document.body.innerHTML = "<h2>Person not found.</h2>";
        return;
    }

    const cardUrl = person.url || `${window.location.origin}${window.location.pathname}?id=${encodeURIComponent(id)}`;

    document.getElementById("name").innerText = person.name;
    document.getElementById("title").innerText = person.title;
    document.getElementById("company").innerText = person.company;
    document.getElementById("photo").src = person.photo;
    document.getElementById("photo").alt = person.name;
    document.getElementById("cardUrl").innerText = cardUrl;

    document.getElementById("callBtn").href = "tel:+" + person.phone;
    document.getElementById("waBtn").href = "https://wa.me/" + person.whatsapp;
    document.getElementById("emailBtn").href = "mailto:" + person.email;
    document.getElementById("websiteBtn").href = person.website;
    document.getElementById("contactBtn").href = person.vcf;

    document.getElementById("copyLinkBtn").addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(cardUrl);
            document.getElementById("copyLinkBtn").innerText = "Copied";
            setTimeout(() => {
                document.getElementById("copyLinkBtn").innerText = "Copy Link";
            }, 1600);
        } catch (error) {
            window.prompt("Copy this e-name card URL:", cardUrl);
        }
    });

});
