const lockScreen = document.getElementById("lockScreen");
const flowerScreen = document.getElementById("flowerScreen");
const letterScreen = document.getElementById("letterScreen");

const dots = document.querySelectorAll("#pinDots span");
const error = document.getElementById("error");

let pin = "";


/* ================= PIN DOTS ================= */

function updateDots() {

    dots.forEach((dot, index) => {

        if (index < pin.length) {
            dot.classList.add("filled");
        } else {
            dot.classList.remove("filled");
        }

    });

}


/* ================= CHECK PIN ================= */

async function checkPin() {

    try {

        const slug = window.location.pathname.split("/")[2];

        if (!slug) {
            error.textContent = "Invalid letter link ❤️";
            return;
        }

        const response = await fetch(`/api/verify/${slug}`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                pin: pin
            })

        });

        const result = await response.json();


        if (result.ok) {

            // Load custom letter content
            document.getElementById("customTitle").textContent =
                result.title;

            document.getElementById("customMessage").textContent =
                result.message;


            /* PIN screen hide */

            lockScreen.classList.remove("active");


            /* Lotus screen show */

            flowerScreen.classList.add("active");


            /*
                Lotus animation ke baad
                letter screen open hoga.
            */

            setTimeout(() => {

                flowerScreen.classList.remove("active");

                letterScreen.classList.add("active");

            }, 7200);


        } else {

            error.textContent =
                "Wrong PIN ❤️ Try again.";

            pin = "";

            updateDots();

        }

    } catch (errorObject) {

        console.error(errorObject);

        error.textContent =
            "Something went wrong. Please try again.";

    }

}


/* ================= NUMBER BUTTONS ================= */

document
    .querySelectorAll(".keypad button[data-key]")
    .forEach(button => {

        button.addEventListener("click", () => {

            if (pin.length >= 4) {
                return;
            }

            pin += button.dataset.key;

            updateDots();


            /*
                4 digits complete hone par
                automatically PIN check hoga.
            */

            if (pin.length === 4) {

                setTimeout(() => {

                    checkPin();

                }, 180);

            }

        });

    });


/* ================= BACKSPACE ================= */

document
    .getElementById("backspace")
    .addEventListener("click", () => {

        pin = pin.slice(0, -1);

        error.textContent = "";

        updateDots();

    });


/* ================= MUSIC ================= */

const musicButton =
    document.getElementById("musicBtn");

const song =
    document.getElementById("song");


musicButton.addEventListener("click", async () => {

    try {

        if (song.paused) {

            await song.play();

            musicButton.textContent =
                "🎵 Pause our song";

        } else {

            song.pause();

            musicButton.textContent =
                "🎵 Play our song";

        }

    } catch {

        musicButton.textContent =
            "Add your MP3 in static folder";

    }

});