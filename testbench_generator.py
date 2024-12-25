import re
import re as finder
import tkinter as tk
from tkinter import filedialog, scrolledtext
import customtkinter as ctk

# Global variables for parsed Verilog components
module_name = None
all_ports = {}
all_input_signals = {}
all_output_signals = {}
all_registers_signals = {}
all_wires_signals = {}
assign_dict = {}
always_list = []
all_parameters = {}
clock_flag = False
reset_flag = False


# Helper Functions

def find_Bus_size(Bus):
    """Calculate the size of a bus."""
    if Bus != "1-bit":
        Bus_match = re.findall(r"\[\s*(\d+)\s*:\s*(\d+)\s*\]", Bus)
        if Bus_match:
            return abs(int(Bus_match[0][0]) - int(Bus_match[0][1])) + 1
        else:
            raise ValueError(f"Invalid bus format: {Bus}")
    else:
        return 1


def parse_file(filename):
    """Parse the Verilog file and populate global variables."""
    global module_name, all_ports, all_input_signals, all_output_signals
    global all_registers_signals, all_wires_signals, assign_dict
    global always_list, all_parameters, clock_flag, reset_flag
    with open(filename, 'r') as file:
        verilog_code = file.read()

    print("Module Details: \n")
    ############# module name ##########
    module_match = finder.search(r"module\s+(\w+)", verilog_code)

    if module_match:
        module_name = module_match.group(1)  # Extract the module name

        print(f"Module name: {module_name}")
    else:
        print("No module name found.")
        exit(1)
    #if __name__ == "__main__":
    print("_____________________________________________________")

    ############# Ports Finding Section ##########
    # Regex to find inline ports within the module declaration
    ports_match = finder.search(r"module\s+\w+\s*\((.*?)\);", verilog_code, re.DOTALL)

    all_ports = {}  # To store all port declarations
    if ports_match:
        ports = ports_match.group(1)

        # Match input ports
        port_inputs_match = finder.findall(r"input\s+(\[\s*\d+\s*:\s*\d+\s*\])?\s*(\w+)", ports, re.MULTILINE)
        if port_inputs_match:
            for match in port_inputs_match:
                bus_size = match[0].strip() if match[0] else "1-bit"
                signal = match[1].strip()  # Single signal name
                all_ports[signal] = {"bus_size": bus_size, "direction": "input"}

        # Match output ports
        port_outputs_match = finder.findall(r"output\s+(\[\s*\d+\s*:\s*\d+\s*\])?\s*(\w+)", ports, re.MULTILINE)
        if port_outputs_match:
            for match in port_outputs_match:
                bus_size = match[0].strip() if match[0] else "1-bit"
                signal = match[1].strip()  # Single signal name
                all_ports[signal] = {"bus_size": bus_size, "direction": "output"}




    #if __name__ == "__main__":
    print("Ports Found:")

    for signal, ports in all_ports.items():
        print(f"\t{signal}: {ports['bus_size']}")

    print("_____________________________________________________")

    ############# Inputs and Outputs Dictionaries ##########
    all_input_signals = {}
    all_output_signals = {}

    # Add ports to inputs and outputs dictionaries with type defaults
    for signal, details in all_ports.items():
        if details["direction"] == "input":
            all_input_signals[signal] = {"bus_size": details["bus_size"], "type": "wire"}
        elif details["direction"] == "output":
            all_output_signals[signal] = {"bus_size": details["bus_size"], "type": "reg"}

    # Block-level inputs and outputs
    inputs_match = finder.findall(
        r"^\s*input\s*(wire|reg)?\s*(\[\s*\d+\s*:\s*\d+\s*\])?\s*([\w\s,]+);", verilog_code, re.MULTILINE
    )

    outputs_match = finder.findall(
        r"^\s*output\s*(wire|reg)?\s*(\[\s*\d+\s*:\s*\d+\s*\])?\s*([\w\s,]+);", verilog_code, re.MULTILINE
    )

    # Process block-level inputs
    for match in inputs_match:
        signal_type = match[0].strip() if match[0] else "wire"
        bus_size = match[1].strip() if match[1] else "1-bit"
        signals = [signal.strip() for signal in match[2].split(",")]
        for signal in signals:
            all_input_signals[signal] = {"bus_size": bus_size, "type": signal_type}

    # Process block-level outputs
    for match in outputs_match:
        signal_type = match[0].strip() if match[0] else "reg"
        bus_size = match[1].strip() if match[1] else "1-bit"
        signals = [signal.strip() for signal in match[2].split(",")]
        for signal in signals:
            all_output_signals[signal] = {"bus_size": bus_size, "type": signal_type}

    # Print inputs
    #if __name__ == "__main__":
    print("inputs:")
    for signal, details in all_input_signals.items():
        print(f"input Signal: {signal}, Bus Size: {details['bus_size']}, Type: {details['type']}")
    print("_____________________________________________________")

    # Print outputs
    #if __name__ == "__main__":

    print("outputs:")
    for signal, details in all_output_signals.items():
        print(f"output Signal: {signal}, Bus Size: {details['bus_size']}, Type: {details['type']}")
    print("_____________________________________________________")

    ############### Registers #########

    registers_match = finder.findall(r"reg\s*(\[\s*\d+\s*:\s*\d+\s*\])?\s*([\w\s,]+);", verilog_code)

    all_registers_signals = {}

    # Process matches
    for match in registers_match:
        bus_size = match[0].strip() if match[0] else "1-bit"
        registers_signals = [signal.strip() for signal in match[1].split(",")]

        # Add each signal and its bus size to the dictionary
        for signal in registers_signals:
            all_registers_signals[signal] = bus_size

    #if __name__ == "__main__":
    print("registers:")
    for signal, size in all_registers_signals.items():
        print(f"register Signal: {signal}, Bus Size: {size}")

    print("_____________________________________________________")

    ############### Wires #########

    wires_match = finder.findall(r"wire\s*(\[\s*\d+\s*:\s*\d+\s*\])?\s*([\w\s,]+);", verilog_code)

    all_wires_signals = {}

    # Process matches
    for match in wires_match:
        bus_size = match[0].strip() if match[0] else "1-bit"
        wire_signals = [signal.strip() for signal in match[1].split(",")]

        # Add each signal and its bus size to the dictionary
        for signal in wire_signals:
            all_wires_signals[signal] = bus_size

    #if __name__ == "__main__":
    print("wires:")
    for signal, size in all_wires_signals.items():
        print(f"wire Signal: {signal}, Bus Size: {size}")

    print("_____________________________________________________")

    ############## assign statements ###################
    assign_statements = finder.findall(r"assign\s+(\w+)\s*=\s*(.+?);", verilog_code)

    # Process matches
    assign_dict = {}
    for match in assign_statements:
        lhs = match[0].strip()  # Left-hand side
        rhs = match[1].strip()  # Right-hand side
        assign_dict[lhs] = rhs  # Store in dictionary

    #if __name__ == "__main__":
    print("assign statements:")
    for lhs, rhs in assign_dict.items():
        print(f"Signal: {lhs}, Expression: {rhs}")
    print("______________________________________________________")

    ################ logical operators ####################
    pattern = r"(\w+)\s*=\s*(\w+)\s*([&|^!]{1,2})\s*(\w+)?;"

    # Find all matches in the Verilog code
    matches = re.findall(pattern, verilog_code)

    # Dictionary to store the outputs
    logical_operations = {}

    # Process matches
    for match in matches:
        output_var = match[0]
        operand1 = match[1]
        operator = match[2]
        operand2 = match[3] if match[3] else ""  # Operand2 may be empty for NOT operations

        # Store the operation details in the dictionary
        logical_operations[output_var] = {
            "operand1": operand1,
            "operator": operator,
            "operand2": operand2 if operand2 else "N/A"
        }

    # Print the operations
    print("logical_operations:")
    for var, details in logical_operations.items():
        print(f"{var} = {details['operand1']} {details['operator']} {details['operand2']}")
    print("______________________________________________________")
    ############## Always Blocks ###################

    always_blocks = finder.findall(
        r"always\s*@\s*(\([^\)]*\))\s*begin(.*?)end\s*(?=always|endmodule|$)",
        verilog_code,
        re.DOTALL
    )

    always_list = []
    for match in always_blocks:
        sensitivity_list = match[0].strip()
        block_body = match[1].strip()
        always_list.append((sensitivity_list, block_body))
    #if __name__ == "__main__":
    print("always blocks:")
    for idx, (sensitivity, body) in enumerate(always_list, start=1):
        print(f"Always Block {idx}:")
        print(f"  Sensitivity List: {sensitivity}")
        print(f"  Body:\n{body}")
        print("------------------------------------------------------")

    ############## If Statements ###################

    # Match if-else structures, including nested ones, with or without begin-end
    if_statements = finder.findall(
        r"if\s*\(([^)]+)\)\s*(begin.*?end|[^;]+;)(\s*else\s*(if\s*\(([^)]+)\)\s*(begin.*?end|[^;]+;)|begin.*?end|[^;]+;)*)*",
        verilog_code,
        re.DOTALL
    )

    def parse_if_else(statement):
        """
        Recursively parse if-else statements, capturing the condition and body.
        """
        structure = []
        matches = finder.findall(
            r"if\s*\(([^)]+)\)\s*(begin.*?end|[^;]+;)(\s*else\s*(if\s*\(([^)]+)\)\s*(begin.*?end|[^;]+;)|begin.*?end|[^;]+;)*)*",
            statement,
            re.DOTALL
        )
        for match in matches:
            condition = match[0].strip()
            body = match[1].strip()
            else_part = match[2].strip() if match[2] else None
            else_structure = None
            if else_part:
                if "if" in else_part:
                    else_structure = parse_if_else(else_part)
                else:
                    else_structure = {"else_body": else_part}
            structure.append({
                "if_condition": condition,
                "if_body": body,
                "else_structure": else_structure,
            })
        return structure

    parsed_if_statements = parse_if_else(verilog_code)

    def display_if_statements(statements, indent=0):
        """
        Display parsed if-else statements in a readable format.
        """
        spacing = "  " * indent
        #if __name__ == "__main__":
        for stmt in statements:
            print(f"{spacing}If Condition: {stmt['if_condition']}")
            print(f"{spacing}If Body: {stmt['if_body']}")
            if stmt['else_structure']:
                if isinstance(stmt['else_structure'], list):
                    print(f"{spacing}else:")
                    display_if_statements(stmt['else_structure'], indent + 1)
            #else:
            #print(f"{spacing}else Body: {stmt['else_structure']['else_body']}")

    #if __name__ == "__main__":

    print("If Statements:")
    display_if_statements(parsed_if_statements)
    #if __name__ == "__main__":
    print("______________________________________________________")

    ############# parameters ############

    # Regex to match parameters, including complex values and optional comments
    parameters_match = finder.findall(
        r"parameter\s+(\w+)\s*=\s*([^;]+);",  # Match everything until the semicolon
        verilog_code,
        re.MULTILINE
    )

    all_parameters = {}

    # Process each match
    for match in parameters_match:
        parameter_name = match[0].strip()  # Capture the parameter name
        parameter_value = match[1].strip()  # Capture the parameter value (allowing complex expressions)
        all_parameters[parameter_name] = parameter_value

    # Print the collected parameters
    #if __name__ == "__main__":
    print("Parameters:")
    for parameter_name, parameter_value in all_parameters.items():
        print(f"Parameter: {parameter_name}, Value: {parameter_value}")

    print("______________________________________________________")

    ############ flags ###############
    clock_flag, reset_flag = False, False

    # Check for clock signals
    if "clock" in all_input_signals or "clk" in all_input_signals:
        clock_flag = True

    # Check for reset signals
    if "reset" in all_input_signals or "rst" in all_input_signals:
        reset_flag = True



    #if __name__ == "__main__":
    print(f"Flags:\n Clock is {clock_flag} \n reset is {reset_flag}")



def parse_data(verilog_file):
    """Generate a detailed report of the parsed data."""
    with open(verilog_file, 'r') as file:
        verilog_code = file.read()

    parsed_data = f"Module Name: {module_name}\n\n"
    parsed_data += "Inputs:\n"
    parsed_data += ''.join(
        [f"  {signal}: {find_Bus_size(details['bus_size'])} bits ({details['type']})\n" for signal, details in all_input_signals.items()]
    )
    parsed_data += "\nOutputs:\n"
    parsed_data += ''.join(
        [f"  {signal}: {find_Bus_size(details['bus_size'])} bits ({details['type']})\n" for signal, details in all_output_signals.items()]
    )
    parsed_data += "\nParameters:\n"
    parsed_data += ''.join([f"  {param}: {value}\n" for param, value in all_parameters.items()])
    parsed_data += "\nFlags:\n"
    parsed_data += f"  Clock: {'Yes' if clock_flag else 'No'}\n"
    parsed_data += f"  Reset: {'Yes' if reset_flag else 'No'}\n"

    return parsed_data


def generate_testbench():

    ####### timescale and test bench name ########
    time_scale = "`timescale 1ns / 1ps"
    tb_module_name = module_name + "_tb;"

    ########## input registers #########
    input_statements = "\n"
    for signal, details in all_input_signals.items():
        # Determine type (`reg` or `wire`) for the input signal
        signal_type = "reg" if details['type'] == "wire" else "wire"
        bus_size = f"{details['bus_size']} " if details['bus_size'] != "1-bit" else ""
        input_statements += f"{signal_type} {bus_size}{signal};\n"

    #print("Input Declarations:")
    #print(input_statements)
    ####################### Output Wires ######################
    output_statements = "\n"
    for signal, details in all_output_signals.items():
        # Determine type (`reg` or `wire`) for the input signal
        signal_type = "reg" if details['type'] == "wire" else "wire"
        bus_size = f"{details['bus_size']} " if details['bus_size'] != "1-bit" else ""
        output_statements += f"{signal_type} {bus_size}{signal};\n"

    #print("output Declarations:")
    #print(output_statements)

    ############ module instantiation ###########

    #instantiate module with name dut
    module_instantiation = f"\n{module_name} dut(\n"
    #add inputs
    for signal, details in all_input_signals.items():
        module_instantiation += f".{signal}({signal}),\n"
    #add outputs
    for signal, details in all_output_signals.items():
        module_instantiation += f".{signal}({signal}),\n"
    #remove last comma
    module_instantiation = module_instantiation.rstrip(",\n")
    # add last bracket and comma
    module_instantiation += "\n);\n"

    #print(module_instantiation)

    ############ clock writing ############
    clock_statements = ""
    clock_signal = "clk" if "clk" in all_input_signals else "clock"
    if clock_flag:



        # Generate the clock statements
        clock_statements += f"""
        initial begin
            // Generate clock
            {clock_signal} = 0;
            forever #1 {clock_signal} = ~{clock_signal};
        end
        """

    # Print the generated clock statements
    #print(clock_statements)
    if reset_flag:
        reset_signal = "rst" if "rst" in all_input_signals else "reset"
    else:
        reset_signal = ""

    ########## monitor statement ##########
    # Creating the monitor block
    monitor_statement = """
    initial
    begin
        $monitor(\""""

    # Add input signals to the format string
    for signal in all_input_signals.keys():
        if not signal == clock_signal:
            monitor_statement += f"{signal} = %b, "

    # Add output signals to the format string
    for signal in all_output_signals.keys():
        monitor_statement += f"{signal} = %b, "

    # Remove the trailing comma and space
    monitor_statement = monitor_statement.rstrip(", ")

    monitor_statement += "\", "
    for signal in all_input_signals.keys():
        if not signal == clock_signal:
            monitor_statement += f"{signal}, "
    for signal in all_output_signals.keys():
        monitor_statement += f"{signal}, "

    # Remove the trailing comma and space
    monitor_statement = monitor_statement.rstrip(", ")

    # Close the monitor statement
    monitor_statement += ");\nend\n"
    if reset_flag:
        reset_code_1 = f"{reset_signal} = 1;\n"
        reset_code_0 = f"{reset_signal} = 0;\n"
    else:
        reset_code_1 = ""
        reset_code_0 = ""
    # Phase 4: Assign every possible combination to the inputs
    walking_ones = "\n".join([
        f"#10;\n" +
        "\n".join([
            f"{port} = {((combination >> bit_offset) & ((1 << find_Bus_size(details['bus_size'])) - 1))};"
            for bit_offset, (port, details) in enumerate(all_input_signals.items())
            if port != clock_signal and port != reset_signal
        ])
        for combination in range(2 ** sum([find_Bus_size(details['bus_size']) for port, details in all_input_signals.items() if port != clock_signal and port != reset_signal]))
    ])

    #print(monitor_statement)
    test_stimulus = f"""
//*******************************************
// Stimulus Generator
//*******************************************

// Phase 1: Reset Phase
// Initialize all inputs to 0 and assert reset
{reset_code_1} // Assert reset
{ ';'.join([f'{port} = 0' for port in all_input_signals.keys() if port != clock_signal and port != reset_signal])};

                    // Phase 2: Release Reset
// Wait for 100ns to ensure proper reset propagation
#100 {reset_code_0} 

// Phase 3: Basic Test Cases
// Test Case 1: Verify behavior with all inputs set to 0
#10;
{ ';'.join([f'{port} = 0' for port in all_input_signals.keys() if port != clock_signal and port != reset_signal])};

                      // Test Case 2: Verify behavior with all inputs set to 1
#10;
{ ';'.join([f'{port} = 1' for port in all_input_signals.keys() if port != clock_signal and port != reset_signal])};

                      // Test Case 3: Verify behavior with random input combinations
#10;
{ ';'.join([f'{port} = $random' for port in all_input_signals.keys() if port != clock_signal and port != reset_signal])};

                            // Phase 4: Walking Ones Pattern
// Systematically test each combination of inputs
{walking_ones}
"""




    ########## parameters definition #################
    parameters_inst = ";\n".join([f"    {parameter} = {value} "for parameter, value in all_parameters.items()])
    parameters_inst += ";" if not parameters_inst == "" else ""


    # Modify the test_bench_code to use the new test_stimulus
    test_bench_code = f"""
{time_scale}
 module   {tb_module_name}
    //INPUTS
        {input_statements}
    //OUTPUTS
        {output_statements}
    //Instantiate
        {module_instantiation}
    //parameters
{parameters_inst}    
    integer i;
    //clock generation
    {clock_statements}
    initial
        begin
        {test_stimulus}
        
        // Phase 5: Extended Random Testing
        // Additional random test cases to catch corner cases
        
        for (i = 0; i < 20; i = i + 1) begin
            #10;
            { ';\n        '.join([f'{port} = $random' for port in all_input_signals.keys() if port != clock_signal and port != reset_signal])};
        end
        
        // Phase 6: Test Completion
        // Allow for final signals to propagate and end simulation
        #100; $finish;
    end
            
        //monitor the results
        {monitor_statement}
    endmodule
    """
    print(test_bench_code)
    return test_bench_code



# GUI Implementation
class TestbenchGeneratorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Verilog Testbench Generator")
        self.geometry("900x600")

        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.parsed_data = ""

        ctk.CTkLabel(self, text="Verilog Input File:").grid(row=0, column=0, padx=30, pady=20, sticky="w")
        ctk.CTkEntry(self, textvariable=self.input_file, width=525).grid(row=0, column=1, padx=10, pady=20, sticky="w")
        ctk.CTkButton(self, text="Browse", command=self.select_input_file).grid(row=0, column=2, padx=10, pady=20, sticky="e")

        ctk.CTkLabel(self, text="Output Testbench File:").grid(row=1, column=0, padx=30, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=self.output_file, width=525).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkButton(self, text="Browse", command=self.select_output_file).grid(row=1, column=2, padx=10, pady=10, sticky="e")

        ctk.CTkButton(self, text="Generate Testbench", command=self.parse_and_generate).grid(row=2, column=1, pady=20)

        ctk.CTkLabel(self, text="Parsed Data:").grid(row=3, column=0, padx=10, pady=10, sticky="nw")
        self.data_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20, width=100, font=("Arial", 12))
        self.data_display.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        self.status_label = tk.Label(self, text="", font=("Arial", 12), fg="green")
        self.status_label.grid(row=4, column=1, pady=10)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Verilog Files", "*.v")])
        if file_path:
            self.input_file.set(file_path)

    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".v", filetypes=[("Verilog Files", "*.v")])
        if file_path:
            self.output_file.set(file_path)

    def parse_and_generate(self):
        input_path = self.input_file.get()
        output_path = self.output_file.get()

        if not input_path:
            self.update_status("Please select a Verilog input file.", "red")
            return

        if not output_path:
            self.update_status("Please select an output file.", "red")
            return

        try:
            parse_file(input_path)

            self.data_display.delete(1.0, tk.END)
            self.data_display.insert(tk.END, parse_data(input_path))

            test_bench_code = generate_testbench()

            with open(output_path, 'w') as output_file:
                output_file.write(test_bench_code)

            self.update_status("Testbench generated successfully!", "green")

        except Exception as e:
            self.update_status(f"Error: {e}", "red")

    def update_status(self, message, color):
        self.status_label.config(text=message, fg=color)


if __name__ == "__main__":
    app = TestbenchGeneratorGUI()
    app.mainloop()
