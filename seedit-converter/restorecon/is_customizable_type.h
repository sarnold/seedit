#ifdef COS4
#define NO_CUSTOMIZABLE_TYPES
#endif
#ifdef AX2
#define NO_CUSTOMIZABLE_TYPES
#endif

#ifdef NO_CUSTOMIZABLE_TYPES
int is_context_customizable(security_context_t context);
#endif
