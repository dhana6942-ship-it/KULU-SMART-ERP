c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Verify & Save Changes"):
                            if e_otp == st.session_state.admin_otp:
                                d = st.session_state.update_data
                                try:
                                    # Database update inside try block
                                    run_query("UPDATE users SET email=?, mobile=?, password=? WHERE email=?", 
                                              (d['email'], d['mobile'], d['pass'], st.session_state.user_email))
                                    st.success("🎉 Profile & Password Updated Successfully!")
                                    st.session_state.user_email = d['email'] # Update active session ID
                                    st.session_state.admin_update_step = 1
                                    st.rerun()
                                except sqlite3.IntegrityError:
                                    # Yeh error message dikhayega agar email duplicate hua
                                    st.error("❌ Yeh Email ID pehle se hi kisi aur account mein registered hai. Kripya naya ya dusra email dein!")
                            else:
                                st.error("❌ Invalid OTP. Try again.")
                    with c2:
                        if st.button("🚫 Cancel"):
                            st.session_state.admin_update_step = 1
                            st.rerun()
