$(document).ready(function () {
    var socket = io();

    socket.on("bot_response", function (message) {
        $("#chat-box").append("<p><strong>Bot:</strong> " + message + "</p>");
        $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
    });

    socket.on("update_seat", function (seat) {
        var seatDiv = $("#seat-" + seat.seat_number);
        seatDiv.removeClass("available male female selected");
        if (seat.status === "available") {
            seatDiv.addClass("available");
        } else if (seat.status === "male") {
            seatDiv.addClass("male");
        } else if (seat.status === "female") {
            seatDiv.addClass("female");
        } else if (seat.status === "selected") {
            seatDiv.addClass("selected");
        }
    });

    $("#chat-input").keypress(function (e) {
        if (e.which == 13) {
            var message = $("#chat-input").val();
            $("#chat-box").append(
                "<p><strong>You:</strong> " + message + "</p>"
            );
            $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
            socket.emit("chat_message", {
                message: message,
                gender: window.userGender,
            });
            $("#chat-input").val("");
        }
    });

    function loadSeats() {
        $.get("/get_seats", function (data) {
            var seatContainer = $("#seat-container");
            seatContainer.empty();

            // Create rows with seats
            for (var i = 1; i <= 40; i += 4) {
                var row = $("<div class='seat-row'></div>");

                for (var j = 0; j < 2; j++) {
                    var seatLeft = data.find((seat) => seat.seat_number === i + j);
                    var seatRight = data.find(
                        (seat) => seat.seat_number === i + j + 2
                    );

                    var seatDivLeft = $("<div></div>")
                        .attr("id", "seat-" + seatLeft.seat_number)
                        .addClass("seat")
                        .text(seatLeft.seat_number)
                        .addClass(
                            seatLeft.status === "available"
                                ? "available"
                                : seatLeft.status
                        );

                    var seatDivRight = $("<div></div>")
                        .attr("id", "seat-" + seatRight.seat_number)
                        .addClass("seat")
                        .text(seatRight.seat_number)
                        .addClass(
                            seatRight.status === "available"
                                ? "available"
                                : seatRight.status
                        );

                    row.append(seatDivLeft);
                }

                row.append("<div class='seat gap'></div>");

                for (var j = 0; j < 2; j++) {
                    var seat = data.find((seat) => seat.seat_number === i + j + 2);

                    var seatDiv = $("<div></div>")
                        .attr("id", "seat-" + seat.seat_number)
                        .addClass("seat")
                        .text(seat.seat_number)
                        .addClass(
                            seat.status === "available" ? "available" : seat.status
                        );

                    row.append(seatDiv);
                }

                seatContainer.append(row);
                seatContainer.append("<div class='row-gap'></div>");
            }

            // Last row with 5 seats
            var lastRow = $("<div class='seat-row'></div>");
            for (var i = 41; i <= 45; i++) {
                var seat = data.find((seat) => seat.seat_number === i);

                var seatDiv = $("<div></div>")
                    .attr("id", "seat-" + seat.seat_number)
                    .addClass("seat")
                    .text(seat.seat_number)
                    .addClass(
                        seat.status === "available" ? "available" : seat.status
                    );

                lastRow.append(seatDiv);
            }
            seatContainer.append(lastRow);
        });
    }

    loadSeats();
});
