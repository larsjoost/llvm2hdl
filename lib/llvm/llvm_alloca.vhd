library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.llvm_pkg.integer_array_t;
use work.llvm_pkg.c_integer_array_default;

entity llvm_alloca is
  generic (
    size           : positive;
    initialization : integer_array_t := c_integer_array_default
    );
  port (
    a         : out std_ulogic_vector;
    s_araddr  : in  std_ulogic_vector;
    s_arid    : in  std_ulogic_vector;
    s_arvalid : in  std_ulogic;
    s_arready : out std_ulogic;
    s_rdata   : out std_ulogic_vector;
    s_rid     : out std_logic_vector;
    s_rvalid  : out std_ulogic;
    s_rready  : in  std_ulogic;
    s_awaddr  : in  std_ulogic_vector;
    s_awid    : in  std_ulogic_vector;
    s_awvalid : in  std_ulogic;
    s_awready : out std_ulogic;
    s_wready  : out std_ulogic;
    s_wvalid  : in  std_ulogic;
    s_wdata   : in  std_ulogic_vector;
    s_wid     : in  std_ulogic_vector;
    s_bready  : in  std_ulogic;
    s_bvalid  : out std_ulogic;
    s_bid     : out std_ulogic_vector;
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    s_tvalid  : in  std_ulogic;
    s_tready  : out std_ulogic;
    s_tag     : in  std_ulogic_vector;
    m_tag     : out std_ulogic_vector;
    m_tvalid  : out std_ulogic;
    m_tready  : in  std_ulogic
    );
end entity llvm_alloca;

architecture rtl of llvm_alloca is

  constant c_data_width : positive := s_wdata'length;

  constant c_size : positive := size * 8 / c_data_width;

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

  signal memory_i : memory_t := get_initialization;

  signal araddr_i, awaddr_i : integer range 0 to c_size - 1;

  signal wdata_transfer_i : std_ulogic;

begin

  araddr_i <= to_integer(unsigned(s_araddr)) mod c_size;

  awaddr_i <= to_integer(unsigned(s_awaddr)) mod c_size;

  s_arready <= '1';

  s_awready <= '1';

  s_wready <= '1';

  wdata_transfer_i <= s_wvalid and s_bready;

  process (clk)
  begin
    if rising_edge(clk) then
      if s_wready = '1' then
        memory_i(awaddr_i) <= s_wdata;
      end if;
      s_rdata  <= memory_i(araddr_i);
      s_rid    <= s_arid;
      s_rvalid <= s_arvalid;
      if s_bready = '1' then
        s_bvalid <= '0';
      end if;
      if wdata_transfer_i = '1' then
        s_bvalid <= '1';
        s_bid    <= s_wid;
      end if;
    end if;
  end process;

  s_tready <= m_tready;

  m_tvalid <= s_tvalid;

  m_tag <= s_tag;

  a <= std_ulogic_vector(to_unsigned(0, a'length));

end architecture rtl;

