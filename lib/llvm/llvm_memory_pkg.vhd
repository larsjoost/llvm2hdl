
package memory_pkg is

  subtype memory_addr_t is std_ulogic_vector(0 to 63);
  subtype memory_data_t is std_ulogic_vector(0 to 63);
  subtype memory_id_t is std_ulogic_vector(0 to 7);

  type memory_master_t is record
    addr                : memory_addr_t;
    addr_id             : memory_id_t;
    addr_valid          : std_ulogic;
    data_width          : positive;
    data                : memory_data_t;
    data_valid          : std_ulogic;
    data_ready          : std_ulogic;
    data_response_ready : std_ulogic;
  end type memory_master_t;

  type memory_slave_t is record
    addr_ready          : std_ulogic;
    data_ready          : std_ulogic;
    data_valid          : std_ulogic;
    data                : memory_data_t;
    data_id             : memory_id_t;
    data_response_valid : std_ulogic;
    data_response_id    : memory_id_t;
  end type memory_slave_t;

end package memory_pkg;
