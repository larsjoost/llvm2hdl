library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity arbiter is
  port (
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    s_araddr  : in  std_ulogic_vector;
    s_arid    : in  std_ulogic_vector;
    s_arvalid : in  std_ulogic_vector;
    s_arready : out std_ulogic_vector;
    s_rdata   : out std_ulogic_vector;
    s_rid     : out std_logic_vector;
    s_rvalid  : out std_ulogic_vector;
    s_rready  : in  std_ulogic_vector;
    s_awaddr  : in  std_ulogic_vector;
    s_awid    : in  std_ulogic_vector;
    s_awvalid : in  std_ulogic_vector;
    s_awready : out std_ulogic_vector;
    s_wready  : out std_ulogic_vector;
    s_wvalid  : in  std_ulogic_vector;
    s_wdata   : in  std_ulogic_vector;
    s_wid     : in  std_ulogic_vector;
    s_bready  : in  std_ulogic_vector;
    s_bvalid  : out std_ulogic_vector;
    s_bid     : out std_ulogic_vector;
    m_araddr  : out std_ulogic_vector;
    m_arid    : out std_ulogic_vector;
    m_arvalid : out std_ulogic;
    m_arready : in  std_ulogic;
    m_rdata   : in  std_ulogic_vector;
    m_rid     : in  std_logic_vector;
    m_rvalid  : in  std_ulogic;
    m_rready  : out std_ulogic;
    m_awaddr  : out std_ulogic_vector;
    m_awid    : out std_ulogic_vector;
    m_awvalid : out std_ulogic;
    m_awready : in  std_ulogic;
    m_wready  : in  std_ulogic;
    m_wvalid  : out std_ulogic;
    m_wdata   : out std_ulogic_vector;
    m_wid     : out std_ulogic_vector;
    m_bready  : out std_ulogic;
    m_bvalid  : in  std_ulogic;
    m_bid     : in  std_ulogic_vector
    );
end entity arbiter;

architecture rtl of arbiter is

  constant c_size : positive := s_arvalid'length;

  signal grant_i : integer range 0 to c_size - 1;

begin

  

end architecture rtl;
