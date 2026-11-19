# How to Install SCAPL

## Option 1: Using the `.exe` File

1. Make sure **Python** is installed and added to your system **PATH**.
2. Run `SCAPL_IDLE_x.x.x.exe`.
   * **If there is no error:** Go to step 3!
   * **If an error occurs:** Try reinstalling and running it again. If the issue persists, please open an issue with as many details as possible.
3. Close **SCAPL IDLE**.
4. Double-click on `test_config.scapl`.
5. Select **Open with** and choose `SCAPL_IDLE_x.x.x.exe`.
   * **If there is no error message:** Perfect! SCAPL is properly configured—you can start testing or using it!
   * **If an error occurs:** Manually create a `test_config.scapl` file with the following content and try again:

```scapl
load utils
load time

str heure = time.hour()
int a = 1
float b = 2.5
bool c = True

if (a == 2) 
{
    utils.print_("2 : error")
}
elif (b == 5 / 3) 
{
    utils.print_("3 : error")
}
else 
{
    utils.print_("1 : ok")
}

utils.print_("2 : ok")
utils.print_("3 : ok")
utils.print_("If there is no error message, the configuration was successful at ", heure, "!")

## How to Install SCAPL (Building from Source with `.py` and PyInstaller)

1. Make sure **Python** is installed and added to your system **PATH**.
2. Make sure **PyInstaller** is installed (you can install it via `pip install pyinstaller`).
3. Navigate to the source directory.
4. Run the following command in your terminal:
   ```bash
   pyinstaller SCAPL_IDLE.py --onefile --name=<your_chosen_name>
5. Move the generated `.exe` file from the `dist/` folder into the main source directory.
6. Test the `.exe` file:
   * **If it works:** Perfect! You can start using it!
   * **If it doesn't work:** Please open an issue.
