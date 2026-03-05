; ============================================================
; Assignment 3A Part 1 - ADE L Setup Script
; ============================================================

sess = asiGetCurrentSession()

if(sess then
  printf("Configuring ADE L session...\n")

  ; ---------- Design Variables ----------
  asiSetDesignVarList(sess '(
    ("deadtime" "5n")
    ("iload" "2")
    ("fsw" "500k")
    ("nf" "100")
    ("pmos_w" "3u")
    ("nmos_w" "pmos_w*4")
  ))
  printf("Variables set.\n")

  ; ---------- Outputs ----------
  asiSetOutputList(sess '(
    (v "/input")
    (v "/O+")
    (v "/O-")
    (v "/Vgh")
    (v "/Vgl")
    (v "/sw")
    (i "/V3/PLUS")
    (i "/V3/MINUS")
  ))
  printf("Outputs set.\n")

  printf("\n=== Done ===\n")
  printf("Now manually: Analyses > Choose > tran, stop=10u, errpreset=conservative\n")
  printf("Then: Session > Save State > a3a_p1_sims\n")
else
  printf("ERROR: No ADE L session found.\n")
)
