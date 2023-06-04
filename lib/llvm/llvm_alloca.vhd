library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.llvm_pkg.integer_array_t;
use work.llvm_pkg.c_integer_array_default;
use work.llvm_pkg.to_string;

entity llvm_alloca is
  generic (
    size_bytes     : positive;
    initialization : integer_array_t := c_integer_array_default
    );
  port (
    m_tdata   : out std_ulogic_vector;
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

library memory;

architecture rtl of llvm_alloca is

begin

  ram_1 : entity memory.ram
    generic map (
      size_bytes     => size_bytes,
      initialization => initialization)
    port map (
      clk       => clk,
      sreset    => sreset,
      s_araddr  => s_araddr,
      s_arid    => s_arid,
      s_arvalid => s_arvalid,
      s_arready => s_arready,
      s_rdata   => s_rdata,
      s_rid     => s_rid,
      s_rvalid  => s_rvalid,
      s_rready  => s_rready,
      s_awaddr  => s_awaddr,
      s_wready  => s_wready,
      s_wvalid  => s_wvalid,
      s_wdata   => s_wdata,
      s_wid     => s_wid,
      s_bready  => s_bready,
      s_bvalid  => s_bvalid,
      s_bid     => s_bid);

  s_tready <= m_tready;

  m_tvalid <= s_tvalid;

  m_tag <= s_tag;

  m_tdata <= std_ulogic_vector(to_unsigned(0, m_tdata'length));

end architecture rtl;

