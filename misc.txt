SCALE = [9, 11,0, 2, 4, 5, 7]
// A
// B
// C
// D
// E
// F
// G


    private static final String[] VALUE_TO_STRING = {
            "C", "^C", "D", "^D", "E", "F", "^F", "G", "^G", "A", "^A", "B"
    };
    

        public static int numAccidentals(MusicKeys key) {
        switch (key)
        case C:
            return 0;
        case CS:
            return 7;
        case D:
            return 2;
        case Eb:
            return -3;
        case E:
            return 4;
        case F:
            return -1;
        case FS:
            return 6;
        case G:
            return 1;
        case Ab:
            return -4;
        case A:
            return 3;
        case Bb:
            return -2;
        case B:
            return 5;
        default:
            throw new AssertionError();
        }
    }