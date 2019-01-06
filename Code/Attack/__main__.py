from Application import *
from Presentation import *
import tkinter


def main():
    # Create Tkinter window
    root = tkinter.Tk()
    root.title("Crib Dragging Tool")

    # Initialise application models
    data_model = ApplicationModel()
    navigation_model = NavigationModel()

    # Initialise screens
    load_cipher_texts_screen = LoadCipherTextsScreen(root, data_model, navigation_model)
    pair_selection_screen = PairSelectionScreen(root, data_model, navigation_model)
    crib_dragging_screen = CribDraggingScreen(root, data_model, navigation_model)
    navigation_model.add_screen(load_cipher_texts_screen, "Load Cipher Texts")
    navigation_model.add_screen(pair_selection_screen, "Pair Selection")
    navigation_model.add_screen(crib_dragging_screen, "Crib Dragging")

    # Switch to start screen and activate Tkinter window
    navigation_model.show_screen("Load Cipher Texts")
    root.mainloop()


if __name__ == '__main__':
    main()
