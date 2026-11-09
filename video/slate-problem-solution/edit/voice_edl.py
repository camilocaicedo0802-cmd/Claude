# Problem (off-camera voice, Q) -> Solution (presenter, A). Windows cut on measured speech onsets/offsets (NOREFINE=1);
# whisper word starts run 0.1-0.3 s late, so starts were moved back to the real onset.
EDL = [
 ("a", 1.58, 3.12, "Pale or dull skin."),                                   # Q1
 ("a", 3.20, 4.75, "A custom spray tan."),                                  # A1
 ("a", 5.70, 7.28, "Need color ASAP."),                                     # Q2
 ("a", 7.38, 10.10, "We have a rapid formula just for that."),             # A2
 ("a", 11.66, 13.48, "Dry or patchy skin."),                                # Q3
 ("a", 18.03, 21.25, "Exfoliate 24 hours before your appointment."),        # A3
 ("a", 33.96, 35.74, "Tan fading unevenly."),                               # Q4
 ("a", 35.76, 37.30, "Moisturize daily."),                                  # A4
 ("a", 40.70, 43.12, "Tan sticking to hands, feet."),                       # Q5
 ("a", 57.40, 60.82, "We have barrier cream in the room for that before your appointment."),  # A5
 ("b", 2.20, 4.06, "Going on vacation."),                                   # Q6
 ("b", 4.80, 7.86, "Book your spray tan one to two days before your trip."),  # A6
 ("b", 10.84, 12.46, "Wedding or special event."),                          # Q7
 ("b", 29.19, 38.10, "Make sure you book your appointment one to two days before your wedding and follow the prep instructions that we send you, and we'll do a custom shade for you."),  # A7
 ("c", 4.20, 7.30, "Not sure which shade or solution is right for you."),  # Q8
 ("c", 7.80, 11.05, "Every client gets a personalized spray tan consultation."),  # A8
 ("d", 7.08, 10.80, "Every skin tone, undertone, and glow goal is different."),  # C1
 ("d", 13.85, 15.60, "Your spray tan should be too."),                      # C2
 ("d", 19.55, 21.62, "If you relate to any of this,"),                      # C3
 ("d", 22.92, 26.15, "come see us at Slate and we'll find the perfect tan for you."),  # C4
]
ROLE = ["Q","A","Q","A","Q","A","Q","A","Q","A","Q","A","Q","A","Q","A","C","C","C","C"]
CLIPS = {"a": "IMG_7103", "b": "IMG_7106", "c": "IMG_7108", "d": "IMG_7110"}
