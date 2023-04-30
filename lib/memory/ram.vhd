library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library llvm;
use llvm.llvm_pkg.integer_array_t;
use llvm.llvm_pkg.c_integer_array_default;
use llvm.llvm_pkg.to_string;

entity ram is
  generic (
    size_bytes     : positive;
    initialization : integer_array_t := c_integer_array_default
    );
  port (
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    s_araddr  : in  std_ulogic_vector;
    s_arid    : in  std_ulogic_vector;
    s_arvalid : in  std_ulogic;
    s_arready : out std_ulogic;
    s_rdata   : out std_ulogic_vector;
    s_rid     : out std_logic_vector;
    s_rvalid  : out std_ulogic;
    s_rready  : in  std_ulogic;
    s_awaddr  : in  std_ulogic_vector;
    s_wready  : out std_ulogic;
    s_wvalid  : in  std_ulogic;
    s_wdata   : in  std_ulogic_vector;
    s_wid     : in  std_ulogic_vector;
    s_bready  : in  std_ulogic;
    s_bvalid  : out std_ulogic;
    s_bid     : out std_ulogic_vector);
end entity ram;

architecture rtl of ram is

  constant c_data_width : positive := s_wdata'length;

  constant c_size : positive := size_bytes * 8 / c_data_width;

  type memory_t is array (0 to c_size - 1) of std_ulogic_vector(0 to c_data_width - 1);

  function get_initialization
    return memory_t is
    alias init : integer_array_t(0 to initialization'length - 1) is initialization;
    variable x : memory_t;
  begin
    for i in memory_t'range loop
      if i < initialization'length then
        x(i) := std_ulogic_vector(to_signed(init(i), c_data_width));
      else
        x(i) := (others => '0');
      end if;
    end loop;
    return x;
  end function get_initialization;

  signal araddr_i : integer range 0 to c_size - 1;

begin

  araddr_i <= to_integer(unsigned(s_araddr)) mod c_size;

  process (clk) is
    variable memory_v : memory_t := get_initialization;
    variable awaddr_v : integer range 0 to c_size - 1;
  begin
    if rising_edge(clk) then
      awaddr_v := to_integer(unsigned(s_awaddr)) mod c_size;
      if s_wvalid = '1' and s_wready = '1' then
        memory_v(awaddr_v) := s_wdata;
      end if;
      s_rdata  <= memory_v(araddr_i);
      s_rid    <= s_arid;
      s_rvalid <= s_arvalid;
    end if;
  end process;

  s_arready <= '1';

  s_wready <= '1';

  process (clk)
    variable memory_v : memory_t := get_initialization;
  begin
    if rising_edge(clk) then
      if sreset = '1' then
        s_bvalid <= '0';
      else
        if s_bready = '1' then
          s_bvalid <= '0';
        end if;
        if s_wvalid = '1' and (s_bvalid = '0' or s_bready = '1') then
          s_bvalid <= '1';
          s_bid    <= s_wid;
        end if;
      end if;
    end if;
  end process;

  --pragma synthesis_off

  process is
  begin  
    report "Initialization = " & to_string(Initialization);
    wait;
  end process;
  
  --pragma synthesis_on
  
end architecture rtl;

