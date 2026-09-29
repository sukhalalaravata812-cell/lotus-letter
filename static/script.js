const lockScreen = document.getElementById("lockScreen");
const flowerScreen = document.getElementById("flowerScreen");
const letterScreen = document.getElementById("letterScreen");

const dots = document.querySelectorAll("#pinDots span");
const error = document.getElementById("error");

let pin = "";


// =========================
// UPDATE PIN DOTS
// =========================

function updateDots() {

    dots.forEach((dot, index) => {

        if (index < pin.length) {
            dot.classList.add("filled");
        } else {
            dot.classList.remove("filled");
        }

    });

}


// =========================
// CHECK PIN
// =========================

async function checkPin() {

    try {

        const slug =
            window.location.pathname.split("/")[2];

        if (!slug) {

            error.textContent =
                "Invalid letter link ❤️";

            return;
        }


        const response = await fetch(
            `/api/verify/${slug}`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    pin: pin
                })
            }
        );


        const result =
            await response.json();


        if (result.ok) {

            // =========================
            // CUSTOM CONTENT
            // =========================

            document.getElementById(
                "customTitle"
            ).textContent = result.title;


            document.getElementById(
                "customMessage"
            ).textContent = result.message;


            document.getElementById(
                "loveLine1"
            ).textContent =
                result.love_line_1;


            document.getElementById(
                "loveLine2"
            ).textContent =
                result.love_line_2;


            document.getElementById(
                "signature"
            ).textContent =
                result.signature;


            // =========================
            // CUSTOM SONG
            // =========================

            if (result.song_url) {

                const songSource =
                    song.querySelector("source");

                songSource.src =
                    result.song_url;

                song.load();

            }


            // =========================
            // SHOW FLOWER ANIMATION
            // =========================

            lockScreen.classList.remove("active");

            flowerScreen.classList.add("active");


            // =========================
            // SHOW LETTER
            // =========================

            setTimeout(() => {

                flowerScreen.classList.remove(
                    "active"
                );

                letterScreen.classList.add(
                    "active"
                );

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


// =========================
// KEYPAD
// =========================

document
    .querySelectorAll(
        ".keypad button[data-key]"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                if (pin.length >= 4) {
                    return;
                }

                pin += button.dataset.key;

                updateDots();


                if (pin.length === 4) {

                    setTimeout(() => {
                        checkPin();
                    }, 180);

                }

            }
        );

    });


// =========================
// BACKSPACE
// =========================

document
    .getElementById("backspace")
    .addEventListener("click", () => {

        pin = pin.slice(0, -1);

        error.textContent = "";

        updateDots();

    });


// =========================
// MUSIC
// =========================

const musicButton =
    document.getElementById("musicBtn");

const song =
    document.getElementById("song");


musicButton.addEventListener(
    "click",
    async () => {

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

        } catch (errorObject) {

            console.error(errorObject);

            musicButton.textContent =
                "🎵 Song could not play";

        }

    }
);