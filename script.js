const fileInput = document.getElementById('fileInput');
const previewImg = document.getElementById('preview-img');
const placeholder = document.getElementById('placeholder-content');
const statusText = document.getElementById('status-text');

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // --- YANGI QISM: Rasmni ekranda ko'rsatish ---
    const reader = new FileReader();
    reader.onload = (event) => {
        previewImg.src = event.target.result;
        previewImg.style.display = 'block'; // Rasmni ko'rsatish
        placeholder.style.display = 'none'; // Ikonkani yashirish
    };
    reader.readAsDataURL(file);
    // ------------------------------------------

    addLog(`Fayl tahlilga yuborildi...`, 'text-info');

    const formData = new FormData();
    formData.append('file', file);

    try {
        statusText.innerHTML = 'Tizim holati: <span class="text-warning">Tahlil qilinmoqda...</span>';
        
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === "success" && result.data.length > 0) {
            const topMatch = result.data[0];
            
            // Ma'lumotlarni yangilash
            document.querySelector('.fs-4:nth-child(1)').innerText = `${(topMatch.confidence * 100).toFixed(1)}%`;
            document.querySelectorAll('.fs-4')[1].innerText = result.inference_time;
            document.querySelectorAll('.fs-4')[2].innerText = topMatch.class;

            addLog(`Natija: ${topMatch.class} (${(topMatch.confidence * 100).toFixed(1)}%)`, 'text-success');
            statusText.innerHTML = 'Tizim holati: <span class="text-success">Tayyor</span>';
        } else {
            addLog("Ob'ekt topilmadi", "text-warning");
            statusText.innerHTML = 'Tizim holati: <span class="text-info">Tugallandi</span>';
        }
    } catch (error) {
        addLog("Server xatosi!", "text-danger");
        statusText.innerHTML = 'Tizim holati: <span class="text-danger">Xatolik</span>';
    }
});